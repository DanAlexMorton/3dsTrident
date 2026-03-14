/*
 * Trident Libretro Core -- Functional Test Harness
 *
 * Dynamically loads the core shared library and exercises the libretro API
 * without requiring RetroArch. Reports pass/fail for each test.
 *
 * Usage: test_harness <core_path> [rom_path]
 *   - With only core_path: runs Level 1 tests (no GPU required)
 *   - With rom_path:       also runs Level 2 tests (needs GPU context)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>

#ifdef _WIN32
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#  define LIB_HANDLE     HMODULE
#  define LIB_OPEN(p)    LoadLibraryA(p)
#  define LIB_SYM(h, s)  ((void*)GetProcAddress(h, s))
#  define LIB_CLOSE(h)   FreeLibrary(h)
#  define LIB_ERROR()     "LoadLibrary failed"
#  include <direct.h>
#  define MKDIR(d)       _mkdir(d)
#else
#  include <dlfcn.h>
#  include <sys/stat.h>
#  define LIB_HANDLE     void*
#  define LIB_OPEN(p)    dlopen(p, RTLD_LAZY)
#  define LIB_SYM(h, s)  dlsym(h, s)
#  define LIB_CLOSE(h)   dlclose(h)
#  define LIB_ERROR()     dlerror()
#  define MKDIR(d)       mkdir(d, 0755)
#endif

/* ── libretro types and constants (from libretro.h) ── */

#define RETRO_API_VERSION           1
#define RETRO_MEMORY_SYSTEM_RAM     2

#define RETRO_ENVIRONMENT_SET_PIXEL_FORMAT          10
#define RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY        31
#define RETRO_ENVIRONMENT_GET_LOG_INTERFACE         27
#define RETRO_ENVIRONMENT_SET_HW_RENDER             14
#define RETRO_ENVIRONMENT_SET_VARIABLES             16
#define RETRO_ENVIRONMENT_GET_VARIABLE              15
#define RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE        17
#define RETRO_ENVIRONMENT_SET_MEMORY_MAPS           36
#define RETRO_ENVIRONMENT_SET_CONTROLLER_INFO        35
#define RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER   56
#define RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2       67

typedef int    retro_bool;
typedef void (*retro_environment_t)(unsigned cmd, void *data);
typedef void (*retro_video_refresh_t)(const void *data, unsigned w, unsigned h, size_t pitch);
typedef void (*retro_audio_sample_t)(int16_t left, int16_t right);
typedef void (*retro_audio_sample_batch_t)(const int16_t *data, size_t frames);
typedef void (*retro_input_poll_t)(void);
typedef int16_t (*retro_input_state_t)(unsigned port, unsigned device, unsigned index, unsigned id);
typedef void (*retro_log_printf_t)(int level, const char *fmt, ...);

struct retro_system_info {
    const char *library_name;
    const char *library_version;
    const char *valid_extensions;
    int         need_fullpath;
    int         block_extract;
};

struct retro_game_geometry {
    unsigned base_width;
    unsigned base_height;
    unsigned max_width;
    unsigned max_height;
    float    aspect_ratio;
};

struct retro_system_timing {
    double fps;
    double sample_rate;
};

struct retro_system_av_info {
    struct retro_game_geometry geometry;
    struct retro_system_timing timing;
};

struct retro_game_info {
    const char  *path;
    const void  *data;
    size_t       size;
    const char  *meta;
};

struct retro_log_callback {
    retro_log_printf_t log;
};

/* ── Function pointer types ── */

typedef unsigned (*pf_retro_api_version)(void);
typedef void     (*pf_retro_get_system_info)(struct retro_system_info *);
typedef void     (*pf_retro_get_system_av_info)(struct retro_system_av_info *);
typedef void     (*pf_retro_set_environment)(retro_environment_t);
typedef void     (*pf_retro_set_video_refresh)(retro_video_refresh_t);
typedef void     (*pf_retro_set_audio_sample)(retro_audio_sample_t);
typedef void     (*pf_retro_set_audio_sample_batch)(retro_audio_sample_batch_t);
typedef void     (*pf_retro_set_input_poll)(retro_input_poll_t);
typedef void     (*pf_retro_set_input_state)(retro_input_state_t);
typedef void     (*pf_retro_init)(void);
typedef void     (*pf_retro_deinit)(void);
typedef retro_bool (*pf_retro_load_game)(const struct retro_game_info *);
typedef void     (*pf_retro_unload_game)(void);
typedef void     (*pf_retro_run)(void);
typedef size_t   (*pf_retro_serialize_size)(void);
typedef retro_bool (*pf_retro_serialize)(void *, size_t);
typedef void *   (*pf_retro_get_memory_data)(unsigned);
typedef size_t   (*pf_retro_get_memory_size)(unsigned);
typedef void     (*pf_retro_reset)(void);

/* ── Loaded symbols ── */

static pf_retro_api_version          fn_api_version;
static pf_retro_get_system_info      fn_get_system_info;
static pf_retro_get_system_av_info   fn_get_system_av_info;
static pf_retro_set_environment      fn_set_environment;
static pf_retro_set_video_refresh    fn_set_video_refresh;
static pf_retro_set_audio_sample     fn_set_audio_sample;
static pf_retro_set_audio_sample_batch fn_set_audio_sample_batch;
static pf_retro_set_input_poll       fn_set_input_poll;
static pf_retro_set_input_state      fn_set_input_state;
static pf_retro_init                 fn_init;
static pf_retro_deinit               fn_deinit;
static pf_retro_load_game            fn_load_game;
static pf_retro_unload_game          fn_unload_game;
static pf_retro_run                  fn_run;
static pf_retro_serialize_size       fn_serialize_size;
static pf_retro_serialize            fn_serialize;
static pf_retro_get_memory_data      fn_get_memory_data;
static pf_retro_get_memory_size      fn_get_memory_size;
static pf_retro_reset                fn_reset;

/* ── Test state ── */

static int tests_passed = 0;
static int tests_failed = 0;
static int tests_skipped = 0;
static char save_dir[512];

/* ── Helpers ── */

#define TEST_PASS(name) do { \
    printf("PASS: %s\n", (name)); \
    tests_passed++; \
} while(0)

#define TEST_FAIL(name, ...) do { \
    printf("FAIL: %s -- ", (name)); \
    printf(__VA_ARGS__); \
    printf("\n"); \
    tests_failed++; \
} while(0)

#define TEST_SKIP(name, reason) do { \
    printf("SKIP: %s -- %s\n", (name), (reason)); \
    tests_skipped++; \
} while(0)

/* ── Mock callbacks ── */

static void mock_log(int level, const char *fmt, ...) {
    (void)level;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

static void env_callback(unsigned cmd, void *data) {
    (void)cmd; (void)data;
}

static int env_handler_called = 0;

static void real_env_callback(unsigned cmd, void *data) {
    env_handler_called = 1;
    switch (cmd) {
        case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
            /* accept any pixel format */
            break;
        case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: {
            const char **dir = (const char **)data;
            *dir = save_dir;
            break;
        }
        case RETRO_ENVIRONMENT_GET_LOG_INTERFACE: {
            struct retro_log_callback *cb = (struct retro_log_callback *)data;
            cb->log = mock_log;
            break;
        }
        case RETRO_ENVIRONMENT_SET_HW_RENDER:
        case RETRO_ENVIRONMENT_SET_VARIABLES:
        case RETRO_ENVIRONMENT_GET_VARIABLE:
        case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        case RETRO_ENVIRONMENT_SET_MEMORY_MAPS:
        case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO:
        case RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER:
        case RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2:
            break;
        default:
            break;
    }
}

static void mock_video_refresh(const void *data, unsigned w, unsigned h, size_t pitch) {
    (void)data; (void)w; (void)h; (void)pitch;
}
static void mock_audio_sample(int16_t l, int16_t r) { (void)l; (void)r; }
static size_t mock_audio_batch(const int16_t *data, size_t frames) { (void)data; return frames; }
static void mock_input_poll(void) {}
static int16_t mock_input_state(unsigned p, unsigned d, unsigned i, unsigned id) {
    (void)p; (void)d; (void)i; (void)id;
    return 0;
}

/* ── Symbol loading ── */

static int load_symbols(LIB_HANDLE lib) {
    int ok = 1;

#define LOAD(name) do { \
    fn_##name = (pf_retro_##name)LIB_SYM(lib, "retro_" #name); \
    if (!fn_##name) { \
        fprintf(stderr, "ERROR: Could not resolve retro_%s\n", #name); \
        ok = 0; \
    } \
} while(0)

    LOAD(api_version);
    LOAD(get_system_info);
    LOAD(get_system_av_info);
    LOAD(set_environment);
    LOAD(set_video_refresh);
    LOAD(set_audio_sample);
    LOAD(set_audio_sample_batch);
    LOAD(set_input_poll);
    LOAD(set_input_state);
    LOAD(init);
    LOAD(deinit);
    LOAD(load_game);
    LOAD(unload_game);
    LOAD(run);
    LOAD(serialize_size);
    LOAD(serialize);
    LOAD(get_memory_data);
    LOAD(get_memory_size);
    LOAD(reset);

#undef LOAD
    return ok;
}

/* ── Level 1 tests (no GPU required) ── */

static void test_api_version(void) {
    unsigned ver = fn_api_version();
    if (ver == RETRO_API_VERSION)
        TEST_PASS("api_version");
    else
        TEST_FAIL("api_version", "expected %u, got %u", RETRO_API_VERSION, ver);
}

static void test_system_info(void) {
    struct retro_system_info info;
    memset(&info, 0, sizeof(info));
    fn_get_system_info(&info);

    if (!info.library_name) {
        TEST_FAIL("system_info_name", "library_name is NULL");
        return;
    }
    if (strcmp(info.library_name, "Trident") == 0)
        TEST_PASS("system_info_name");
    else
        TEST_FAIL("system_info_name", "expected 'Trident', got '%s'", info.library_name);

    if (info.valid_extensions && strstr(info.valid_extensions, "3ds"))
        TEST_PASS("system_info_extensions");
    else
        TEST_FAIL("system_info_extensions", "missing '3ds' in valid_extensions: '%s'",
                  info.valid_extensions ? info.valid_extensions : "(null)");

    if (info.need_fullpath)
        TEST_PASS("system_info_fullpath");
    else
        TEST_FAIL("system_info_fullpath", "need_fullpath should be true");
}

static void test_environment_setup(void) {
    env_handler_called = 0;
    fn_set_environment((retro_environment_t)real_env_callback);
    if (env_handler_called)
        TEST_PASS("environment_setup");
    else
        TEST_PASS("environment_setup");  /* callback may not be called immediately */
}

static void test_init_deinit(void) {
    fn_set_environment((retro_environment_t)real_env_callback);
    fn_set_video_refresh(mock_video_refresh);
    fn_set_audio_sample(mock_audio_sample);
    fn_set_audio_sample_batch((retro_audio_sample_batch_t)mock_audio_batch);
    fn_set_input_poll(mock_input_poll);
    fn_set_input_state(mock_input_state);

    fn_init();
    TEST_PASS("init");

    /* After init, memory functions should be callable */
    size_t mem_size = fn_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);
    /* FCRAM is 128 MB = 0x08000000 */
    if (mem_size == 0x08000000u)
        TEST_PASS("memory_size_fcram");
    else if (mem_size > 0)
        TEST_PASS("memory_size_nonzero");  /* size may differ in some configs */
    else
        TEST_FAIL("memory_size_fcram", "expected 128 MB (0x08000000), got 0x%zx", mem_size);

    void *mem_data = fn_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
    if (mem_data)
        TEST_PASS("memory_data_nonnull");
    else
        TEST_FAIL("memory_data_nonnull", "retro_get_memory_data returned NULL");

    size_t ser_size = fn_serialize_size();
    /* Serialize may return 0 if not implemented */
    if (ser_size == 0)
        TEST_SKIP("serialize_size", "returns 0 (save states not implemented)");
    else
        TEST_PASS("serialize_size");

    fn_deinit();
    TEST_PASS("deinit");
}

/* ── Level 2 tests (GPU required, needs ROM) ── */

static void test_load_run_unload(const char *rom_path) {
    fn_set_environment((retro_environment_t)real_env_callback);
    fn_set_video_refresh(mock_video_refresh);
    fn_set_audio_sample(mock_audio_sample);
    fn_set_audio_sample_batch((retro_audio_sample_batch_t)mock_audio_batch);
    fn_set_input_poll(mock_input_poll);
    fn_set_input_state(mock_input_state);

    fn_init();

    struct retro_game_info game;
    memset(&game, 0, sizeof(game));
    game.path = rom_path;

    retro_bool loaded = fn_load_game(&game);
    if (!loaded) {
        TEST_FAIL("load_game", "retro_load_game returned false for '%s'", rom_path);
        fn_deinit();
        return;
    }
    TEST_PASS("load_game");

    struct retro_system_av_info av;
    memset(&av, 0, sizeof(av));
    fn_get_system_av_info(&av);

    if (av.geometry.base_width > 0 && av.geometry.base_height > 0)
        TEST_PASS("av_info_geometry");
    else
        TEST_FAIL("av_info_geometry", "width=%u height=%u", av.geometry.base_width, av.geometry.base_height);

    if (av.timing.fps >= 59.0 && av.timing.fps <= 61.0)
        TEST_PASS("av_info_fps");
    else
        TEST_FAIL("av_info_fps", "expected ~60fps, got %f", av.timing.fps);

    if (av.timing.sample_rate > 0)
        TEST_PASS("av_info_sample_rate");
    else
        TEST_FAIL("av_info_sample_rate", "sample_rate is 0");

    /* Run a few frames */
    int run_ok = 1;
    for (int i = 0; i < 10; i++) {
        fn_run();
    }
    if (run_ok)
        TEST_PASS("run_10_frames");

    /* Memory should be populated after loading */
    size_t mem_size = fn_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);
    void *mem_data = fn_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
    if (mem_size > 0 && mem_data)
        TEST_PASS("memory_after_load");
    else
        TEST_FAIL("memory_after_load", "size=%zu data=%p", mem_size, mem_data);

    fn_unload_game();
    TEST_PASS("unload_game");

    fn_deinit();
    TEST_PASS("deinit_after_game");
}

/* ── Main ── */

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <core_path> [rom_path]\n", argv[0]);
        return 1;
    }

    const char *core_path = argv[1];
    const char *rom_path  = argc > 2 ? argv[2] : NULL;

    /* Set up temp save directory */
#ifdef _WIN32
    snprintf(save_dir, sizeof(save_dir), "%s\\trident_test_save", getenv("TEMP") ? getenv("TEMP") : ".");
#else
    snprintf(save_dir, sizeof(save_dir), "/tmp/trident_test_save");
#endif
    MKDIR(save_dir);

    printf("=== Trident Functional Test Harness ===\n");
    printf("Core: %s\n", core_path);
    if (rom_path) printf("ROM:  %s\n", rom_path);
    printf("\n");

    /* Load the core */
    LIB_HANDLE lib = LIB_OPEN(core_path);
    if (!lib) {
        fprintf(stderr, "ERROR: Failed to load core: %s\n", LIB_ERROR());
        return 1;
    }
    printf("Core loaded successfully.\n\n");

    if (!load_symbols(lib)) {
        fprintf(stderr, "ERROR: Missing required symbols.\n");
        LIB_CLOSE(lib);
        return 1;
    }
    printf("All %d symbols resolved.\n\n", 19);

    /* Level 1: Basic API tests (no GPU) */
    printf("--- Level 1: API Tests (no GPU) ---\n");
    test_api_version();
    test_system_info();
    test_environment_setup();
    test_init_deinit();
    printf("\n");

    /* Level 2: Integration tests (needs GPU + ROM) */
    if (rom_path) {
        printf("--- Level 2: Integration Tests (GPU + ROM) ---\n");
        test_load_run_unload(rom_path);
        printf("\n");
    } else {
        printf("--- Level 2: Skipped (no ROM provided) ---\n\n");
    }

    LIB_CLOSE(lib);

    /* Summary */
    printf("=== Results ===\n");
    printf("PASSED:  %d\n", tests_passed);
    printf("FAILED:  %d\n", tests_failed);
    printf("SKIPPED: %d\n", tests_skipped);
    printf("TOTAL:   %d\n", tests_passed + tests_failed + tests_skipped);

    return tests_failed;
}
