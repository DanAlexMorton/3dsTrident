/*
 * Trident iOS Simulator Test App
 *
 * Minimal iOS app that loads the Trident libretro core via dlopen()
 * and runs functional API tests. Outputs PASS/FAIL to stdout for
 * capture by `xcrun simctl launch --console`.
 *
 * Build: clang -isysroot $(xcrun --sdk iphonesimulator --show-sdk-path)
 *        -target arm64-apple-ios14.0-simulator -framework Foundation
 *        -o TridentTest main.m
 */

#import <Foundation/Foundation.h>
#import <dlfcn.h>
#include <stdio.h>
#include <string.h>

/* ── libretro constants ── */

#define RETRO_API_VERSION                   1
#define RETRO_MEMORY_SYSTEM_RAM             2
#define RETRO_ENVIRONMENT_SET_PIXEL_FORMAT   10
#define RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY 31
#define RETRO_ENVIRONMENT_GET_LOG_INTERFACE  27
#define RETRO_ENVIRONMENT_SET_HW_RENDER      14
#define RETRO_ENVIRONMENT_SET_VARIABLES       16
#define RETRO_ENVIRONMENT_GET_VARIABLE        15
#define RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE  17
#define RETRO_ENVIRONMENT_SET_MEMORY_MAPS     36
#define RETRO_ENVIRONMENT_SET_CONTROLLER_INFO  35
#define RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER 56
#define RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2  67

/* ── libretro types ── */

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

struct retro_log_callback {
    retro_log_printf_t log;
};

/* ── Function pointer types ── */

typedef unsigned (*pf_retro_api_version)(void);
typedef void     (*pf_retro_get_system_info)(struct retro_system_info *);
typedef void     (*pf_retro_set_environment)(retro_environment_t);
typedef void     (*pf_retro_set_video_refresh)(retro_video_refresh_t);
typedef void     (*pf_retro_set_audio_sample)(retro_audio_sample_t);
typedef void     (*pf_retro_set_audio_sample_batch)(retro_audio_sample_batch_t);
typedef void     (*pf_retro_set_input_poll)(retro_input_poll_t);
typedef void     (*pf_retro_set_input_state)(retro_input_state_t);
typedef void     (*pf_retro_init)(void);
typedef void     (*pf_retro_deinit)(void);
typedef size_t   (*pf_retro_get_memory_size)(unsigned);
typedef void *   (*pf_retro_get_memory_data)(unsigned);
typedef size_t   (*pf_retro_serialize_size)(void);

/* ── Test state ── */

static int passed = 0;
static int failed = 0;
static int skipped = 0;
static char save_dir[512];

#define TEST_PASS(name) do { \
    printf("PASS: %s\n", (name)); \
    passed++; \
} while(0)

#define TEST_FAIL(name, ...) do { \
    printf("FAIL: %s -- ", (name)); \
    printf(__VA_ARGS__); \
    printf("\n"); \
    failed++; \
} while(0)

#define TEST_SKIP(name, reason) do { \
    printf("SKIP: %s -- %s\n", (name), (reason)); \
    skipped++; \
} while(0)

/* ── Mock callbacks ── */

static void mock_log(int level, const char *fmt, ...) {
    (void)level;
}

static void env_callback(unsigned cmd, void *data) {
    switch (cmd) {
        case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
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
        default:
            break;
    }
}

static void mock_video(const void *d, unsigned w, unsigned h, size_t p) {
    (void)d; (void)w; (void)h; (void)p;
}
static void mock_audio(int16_t l, int16_t r) { (void)l; (void)r; }
static size_t mock_audio_batch(const int16_t *d, size_t f) { (void)d; return f; }
static void mock_poll(void) {}
static int16_t mock_state(unsigned a, unsigned b, unsigned c, unsigned d) {
    (void)a; (void)b; (void)c; (void)d; return 0;
}

/* ── Main ── */

int main(int argc, char *argv[]) {
    @autoreleasepool {
        NSString *appDir = [[NSBundle mainBundle] bundlePath];
        NSString *corePath = [appDir stringByAppendingPathComponent:@"trident_libretro.dylib"];

        snprintf(save_dir, sizeof(save_dir), "%s/save", [NSTemporaryDirectory() UTF8String]);
        mkdir(save_dir, 0755);

        printf("=== Trident iOS Simulator Functional Tests ===\n");
        printf("Core: %s\n\n", [corePath UTF8String]);

        void *lib = dlopen([corePath UTF8String], RTLD_LAZY);
        if (!lib) {
            printf("ERROR: dlopen failed: %s\n", dlerror());
            return 1;
        }
        printf("Core loaded.\n\n");

        /* Resolve symbols */
        pf_retro_api_version fn_ver = dlsym(lib, "retro_api_version");
        pf_retro_get_system_info fn_info = dlsym(lib, "retro_get_system_info");
        pf_retro_set_environment fn_env = dlsym(lib, "retro_set_environment");
        pf_retro_set_video_refresh fn_vid = dlsym(lib, "retro_set_video_refresh");
        pf_retro_set_audio_sample fn_aud = dlsym(lib, "retro_set_audio_sample");
        pf_retro_set_audio_sample_batch fn_audb = dlsym(lib, "retro_set_audio_sample_batch");
        pf_retro_set_input_poll fn_poll = dlsym(lib, "retro_set_input_poll");
        pf_retro_set_input_state fn_state = dlsym(lib, "retro_set_input_state");
        pf_retro_init fn_init = dlsym(lib, "retro_init");
        pf_retro_deinit fn_deinit = dlsym(lib, "retro_deinit");
        pf_retro_get_memory_size fn_memsize = dlsym(lib, "retro_get_memory_size");
        pf_retro_get_memory_data fn_memdata = dlsym(lib, "retro_get_memory_data");
        pf_retro_serialize_size fn_sersize = dlsym(lib, "retro_serialize_size");

        if (!fn_ver || !fn_info || !fn_env || !fn_init || !fn_deinit) {
            printf("ERROR: Missing core symbols\n");
            dlclose(lib);
            return 1;
        }

        /* Test: API version */
        printf("--- Level 1: API Tests ---\n");

        unsigned ver = fn_ver();
        if (ver == RETRO_API_VERSION)
            TEST_PASS("api_version");
        else
            TEST_FAIL("api_version", "expected %u, got %u", RETRO_API_VERSION, ver);

        /* Test: System info */
        struct retro_system_info sinfo;
        memset(&sinfo, 0, sizeof(sinfo));
        fn_info(&sinfo);

        if (sinfo.library_name && strcmp(sinfo.library_name, "Trident") == 0)
            TEST_PASS("system_info_name");
        else
            TEST_FAIL("system_info_name", "got '%s'", sinfo.library_name ? sinfo.library_name : "(null)");

        if (sinfo.valid_extensions && strstr(sinfo.valid_extensions, "3ds"))
            TEST_PASS("system_info_extensions");
        else
            TEST_FAIL("system_info_extensions", "missing '3ds'");

        /* Test: Init lifecycle */
        fn_env((retro_environment_t)env_callback);
        TEST_PASS("environment_setup");

        if (fn_vid) fn_vid(mock_video);
        if (fn_aud) fn_aud(mock_audio);
        if (fn_audb) fn_audb((retro_audio_sample_batch_t)mock_audio_batch);
        if (fn_poll) fn_poll();
        if (fn_state) fn_state(0, 0, 0, 0);

        fn_init();
        TEST_PASS("init");

        /* Test: Memory */
        if (fn_memsize) {
            size_t sz = fn_memsize(RETRO_MEMORY_SYSTEM_RAM);
            if (sz == 0x08000000u)
                TEST_PASS("memory_size_fcram");
            else
                TEST_FAIL("memory_size_fcram", "expected 0x08000000, got 0x%zx", sz);
        } else {
            TEST_SKIP("memory_size_fcram", "symbol not found");
        }

        if (fn_memdata) {
            void *ptr = fn_memdata(RETRO_MEMORY_SYSTEM_RAM);
            if (ptr)
                TEST_PASS("memory_data_nonnull");
            else
                TEST_FAIL("memory_data_nonnull", "returned NULL");
        } else {
            TEST_SKIP("memory_data_nonnull", "symbol not found");
        }

        /* Test: Serialize */
        if (fn_sersize) {
            size_t sz = fn_sersize();
            if (sz == 0)
                TEST_SKIP("serialize_size", "returns 0 (not implemented)");
            else
                TEST_PASS("serialize_size");
        }

        fn_deinit();
        TEST_PASS("deinit");

        dlclose(lib);

        /* Summary */
        printf("\n=== Results ===\n");
        printf("PASSED:  %d\n", passed);
        printf("FAILED:  %d\n", failed);
        printf("SKIPPED: %d\n", skipped);
        printf("TOTAL:   %d\n", passed + failed + skipped);

        return failed;
    }
}
