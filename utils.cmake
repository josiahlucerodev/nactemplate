include(ProcessorCount)

function(check_if_is_root 
		is_root)

	if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
		set(${is_root} TRUE PARENT_SCOPE)
	else()
		set(${is_root} FALSE PARENT_SCOPE)
	endif()

endfunction()

function(test_for_emscripten_compiler 
	test_output)
	if(CMAKE_CXX_COMPILER MATCHES "/em\\+\\+")
		set(${test_output} TRUE PARENT_SCOPE)
	else()
		set(${test_output} FALSE PARENT_SCOPE)
	endif()
endfunction() 


function(exe_emscripten_setup
	target_name
	html_output)
	test_for_emscripten_compiler(is_emscripten)
	if(is_emscripten AND html_output)
		set_target_properties(${target_name} PROPERTIES SUFFIX ".html")
	endif()
endfunction()

function(set_standard_output target_name)
    set_target_properties(${target_name}
        PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    )
endfunction()

function(set_standard_output_sub target_name sub_dir)
    set_target_properties(${target_name}
        PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/${sub_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/${sub_dir}"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/${sub_dir}"
    )
endfunction()

function(configure_parallel_testing)
    ProcessorCount(N)
    
    if(N EQUAL 0)
        message(WARNING "Could not detect number of processors, defaulting to 1")
        set(N 1)
    endif()
    
    set(CTEST_PARALLEL_LEVEL ${N} CACHE INTERNAL "Number of processors to use for testing")
    
    message(STATUS "Configuring tests to run on ${CTEST_PARALLEL_LEVEL} logical processors")
endfunction()

function(set_global_unity_build)
	set(CMAKE_UNITY_BUILD ON CACHE)
endfunction()
