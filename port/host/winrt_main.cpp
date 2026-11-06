/* WinRT / UWP entry point for Xbox Dev Mode.
   Provides WinMain via SDL_main.h, which invokes SDL_RunApp to start the
   CoreApplication and then calls SDL_main (launcher.c) on the application thread. */
#define SDL_PLATFORM_WINRT 1
#define SDL_WINRT_METADATA_FILE_AVAILABLE 1

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
