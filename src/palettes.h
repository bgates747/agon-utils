#pragma once

// 64-color palette (rgba2222 variant)
// Each row is {R, G, B}
static const unsigned char colors64[64][3] = {
    {  0,   0,   0}, //  0 Black
    {170,   0,   0}, //  1 Dark red
    {  0, 170,   0}, //  2 Dark green
    {170, 170,   0}, //  3 Dark yellow
    {  0,   0, 170}, //  4 Dark blue
    {170,   0, 170}, //  5 Dark magenta
    {  0, 170, 170}, //  6 Dark cyan
    {170, 170, 170}, //  7 Light gray
    { 85,  85,  85}, //  8 Gray
    {255,   0,   0}, //  9 Red
    {  0, 255,   0}, // 10 Green
    {255, 255,   0}, // 11 Yellow
    {  0,   0, 255}, // 12 Blue
    {255,   0, 255}, // 13 Magenta
    {  0, 255, 255}, // 14 Cyan
    {255, 255, 255}, // 15 White
    {  0,   0,  85}, // 16 Navy (darkest blue)
    {  0,  85,   0}, // 17 Dark olive green
    {  0,  85,  85}, // 18 Darker teal
    {  0,  85, 170}, // 19 Azure
    {  0,  85, 255}, // 20 Lighter azure
    {  0, 170,  85}, // 21 Spring green
    {  0, 170, 255}, // 22 Sky blue
    {  0, 255,  85}, // 23 Light spring green
    {  0, 255, 170}, // 24 Medium spring green
    { 85,   0,   0}, // 25 Maroon
    { 85,   0,  85}, // 26 Violet
    { 85,   0, 170}, // 27 Indigo
    { 85,   0, 255}, // 28 Electric indigo
    { 85,  85,   0}, // 29 Dark khaki
    { 85,  85, 170}, // 30 Slate blue
    { 85,  85, 255}, // 31 Light slate blue
    { 85, 170,   0}, // 32 Chartreuse
    { 85, 170,  85}, // 33 Medium sea green
    { 85, 170, 170}, // 34 Light sea green
    { 85, 170, 255}, // 35 Deep sky blue
    { 85, 255,   0}, // 36 Lawn green
    { 85, 255,  85}, // 37 Light green
    { 85, 255, 170}, // 38 Pale green
    { 85, 255, 255}, // 39 Pale turquoise
    {170,   0,  85}, // 40 Medium violet
    {170,   0, 255}, // 41 Medium blue
    {170,  85,   0}, // 42 Golden brown
    {170,  85,  85}, // 43 Rosy brown
    {170,  85, 170}, // 44 Medium orchid
    {170,  85, 255}, // 45 Medium purple
    {170, 170,  85}, // 46 Tan
    {170, 170, 255}, // 47 Light steel blue
    {170, 255,   0}, // 48 Bright green
    {170, 255,  85}, // 49 Pale lime green
    {170, 255, 170}, // 50 Pale light green
    {170, 255, 255}, // 51 Light cyan
    {255,   0,  85}, // 52 Hot pink
    {255,   0, 170}, // 53 Deep pink
    {255,  85,   0}, // 54 Dark orange
    {255,  85,  85}, // 55 Salmon
    {255,  85, 170}, // 56 Orchid
    {255,  85, 255}, // 57 Bright magenta
    {255, 170,   0}, // 58 Orange
    {255, 170,  85}, // 59 Light salmon
    {255, 170, 170}, // 60 Light pink
    {255, 170, 255}, // 61 Lavender pink
    {255, 255,  85}, // 62 Pale yellow
    {255, 255, 170}  // 63 Light yellow
};

// 63-color palette (Magenta is indended to be coded for transparent)
static const unsigned char colors63[63][3] = {
    {  0,   0,   0}, //  0 Black
    {170,   0,   0}, //  1 Dark red
    {  0, 170,   0}, //  2 Dark green
    {170, 170,   0}, //  3 Dark yellow
    {  0,   0, 170}, //  4 Dark blue
    {170,   0, 170}, //  5 Dark magenta
    {  0, 170, 170}, //  6 Dark cyan
    {170, 170, 170}, //  7 Light gray
    { 85,  85,  85}, //  8 Gray
    {255,   0,   0}, //  9 Red
    {  0, 255,   0}, // 10 Green
    {255, 255,   0}, // 11 Yellow
    {  0,   0, 255}, // 12 Blue
    {  0, 255, 255}, // 13 Cyan
    {255, 255, 255}, // 14 White
    {  0,   0,  85}, // 15 Navy (darkest blue)
    {  0,  85,   0}, // 16 Dark olive green
    {  0,  85,  85}, // 17 Darker teal
    {  0,  85, 170}, // 18 Azure
    {  0,  85, 255}, // 19 Lighter azure
    {  0, 170,  85}, // 20 Spring green
    {  0, 170, 255}, // 21 Sky blue
    {  0, 255,  85}, // 22 Light spring green
    {  0, 255, 170}, // 23 Medium spring green
    { 85,   0,   0}, // 24 Maroon
    { 85,   0,  85}, // 25 Violet
    { 85,   0, 170}, // 26 Indigo
    { 85,   0, 255}, // 27 Electric indigo
    { 85,  85,   0}, // 28 Dark khaki
    { 85,  85, 170}, // 29 Slate blue
    { 85,  85, 255}, // 30 Light slate blue
    { 85, 170,   0}, // 31 Chartreuse
    { 85, 170,  85}, // 32 Medium sea green
    { 85, 170, 170}, // 33 Light sea green
    { 85, 170, 255}, // 34 Deep sky blue
    { 85, 255,   0}, // 35 Lawn green
    { 85, 255,  85}, // 36 Light green
    { 85, 255, 170}, // 37 Pale green
    { 85, 255, 255}, // 38 Pale turquoise
    {170,   0,  85}, // 39 Medium violet
    {170,   0, 255}, // 40 Medium blue
    {170,  85,   0}, // 41 Golden brown
    {170,  85,  85}, // 42 Rosy brown
    {170,  85, 170}, // 43 Medium orchid
    {170,  85, 255}, // 44 Medium purple
    {170, 170,  85}, // 45 Tan
    {170, 170, 255}, // 46 Light steel blue
    {170, 255,   0}, // 47 Bright green
    {170, 255,  85}, // 48 Pale lime green
    {170, 255, 170}, // 49 Pale light green
    {170, 255, 255}, // 50 Light cyan
    {255,   0,  85}, // 51 Hot pink
    {255,   0, 170}, // 52 Deep pink
    {255,  85,   0}, // 53 Dark orange
    {255,  85,  85}, // 54 Salmon
    {255,  85, 170}, // 55 Orchid
    {255,  85, 255}, // 56 Bright magenta
    {255, 170,   0}, // 57 Orange
    {255, 170,  85}, // 58 Light salmon
    {255, 170, 170}, // 59 Light pink
    {255, 170, 255}, // 60 Lavender pink
    {255, 255,  85}, // 61 Pale yellow
    {255, 255, 170}  // 62 Light yellow
};

// 16-color palette
static const unsigned char colors16[16][3] = {
    {  0,   0,   0}, //  0 Black
    {170,   0,   0}, //  1 Dark red
    {  0, 170,   0}, //  2 Dark green
    {170, 170,   0}, //  3 Dark yellow
    {  0,   0, 170}, //  4 Dark blue
    {170,   0, 170}, //  5 Dark magenta
    {  0, 170, 170}, //  6 Dark cyan
    {170, 170, 170}, //  7 Light gray
    { 85,  85,  85}, //  8 Gray
    {255,   0,   0}, //  9 Red
    {  0, 255,   0}, // 10 Green
    {255, 255,   0}, // 11 Yellow
    {  0,   0, 255}, // 12 Blue
    {255,   0, 255}, // 13 Magenta
    {  0, 255, 255}, // 14 Cyan
    {255, 255, 255}, // 15 White
};

// 15-color palette (Magenta is intended to be coded for transparent)
static const unsigned char colors15[15][3] = {
    {  0,   0,   0}, //  0 Black
    {170,   0,   0}, //  1 Dark red
    {  0, 170,   0}, //  2 Dark green
    {170, 170,   0}, //  3 Dark yellow
    {  0,   0, 170}, //  4 Dark blue
    {170,   0, 170}, //  5 Dark magenta
    {  0, 170, 170}, //  6 Dark cyan
    {170, 170, 170}, //  7 Light gray
    { 85,  85,  85}, //  8 Gray
    {255,   0,   0}, //  9 Red
    {  0, 255,   0}, // 10 Green
    {255, 255,   0}, // 11 Yellow
    {  0,   0, 255}, // 12 Blue
    {  0, 255, 255}, // 13 Cyan
    {255, 255, 255}, // 14 White
};