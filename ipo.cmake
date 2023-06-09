macro(enable_ipo)
    if(CMAKE_CXX_COMPILER MATCHES "/em\\+\\+")
        message("can not enable ipo with Emscripten")
    else() 
        include(CheckIPOSupported)
        check_ipo_supported(RESULT result OUTPUT output)
        if(result)
        message("ipo enabled")
            set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
        else()
            message(SEND_ERROR "IPO not supported: ${output}")
        endif()
    endif()
endmacro()