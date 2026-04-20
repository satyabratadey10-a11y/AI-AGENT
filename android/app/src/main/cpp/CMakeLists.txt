cmake_minimum_required(VERSION 3.22.1)

project(aiagent_native)

add_library(
    aiagent-native
    SHARED
    native-lib.cpp
)

find_library(
    log-lib
    log
)

target_link_libraries(
    aiagent-native
    ${log-lib}
)
