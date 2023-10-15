#ifndef CONFIG_HPP
#define CONFIG_HPP

#define DEBUG_MODE

//#define DEBUG_MODE_GLOBAL
//#define EMULATION_MODE_GLOBAL

#define EMULATION_MODE_I2C

#define DEBUG_MODE_PROCESS_CONTROL
//#define DEBUG_MODE_I2C
#define DEBUG_MODE_CAMERA
//#define DEBUG_MODE_IMAGE_PROCESSOR
#define DEBUG_MODE_PROJECTOR
#define DEBUG_MODE_DYNAMIC_IMAGE
//#define DEBUG_MODE_RECIPE

#define PYTHON_SCRIPTS_PATH "../scripts/"

#define MOTOR_SPAN_IN_MILLIMETERS (200)
#define MOTOR_MILLIMETERS_PER_MICROSTEP (5.0/(256*200)) //256 microsteps * 200 steps = one revolution = 5mm
#define MILLIMETERS_PER_PIXEL (0.5/1080)
#define ALIGN_ALPHA (0.1*MILLIMETERS_PER_PIXEL/MOTOR_MILLIMETERS_PER_MICROSTEP)

// ------- modify config above this line; do not modify below this line -------

#ifdef DEBUG_MODE
    #include <cstdio>
    #define DEBUG_OUTPUT(...) do { fprintf(stderr, __VA_ARGS__); } while(0)
#else
    #define DEBUG_OUTPUT(...) do {} while(0)
#endif

#ifdef DEBUG_MODE_GLOBAL
    #define DEBUG_MODE_PROCESS_CONTROL
    #define DEBUG_MODE_I2C
    #define DEBUG_MODE_CAMERA
    #define DEBUG_MODE_IMAGE_PROCESSOR
    #define DEBUG_MODE_PROJECTOR
    #define DEBUG_MODE_DYNAMIC_IMAGE
    #define DEBUG_MODE_RECIPE
#endif

#ifdef EMULATION_MODE_GLOBAL
    #define EMULATION_MODE_I2C
#endif

#endif // CONFIG_HPP
