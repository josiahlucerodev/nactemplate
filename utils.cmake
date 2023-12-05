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
	elseif()
		set(${test_output} FALSE PARENT_SCOPE)
	endif()
endfunction() 

function(exe_emscripten_setup
	html_output)
	test_for_emscripten_compiler(is_emscripten)
	if(is_emscripten AND html_output)
		set(CMAKE_EXECUTABLE_SUFFIX .html PARENT_SCOPE)
	endif()
endfunction()

function(set_standard_output 
	project_name)

	set_target_properties(${project_name}
		PROPERTIES
		ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
		RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
	)
endfunction()
