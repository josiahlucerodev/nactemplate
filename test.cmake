function(set_standard_test_output 
	project_name)

	set_target_properties(${project_name}
		PROPERTIES
		ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/test"
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/test"
		RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/test"
	)
endfunction()

function(nact_add_test TestName)
	if (MSVC)
		target_compile_options(${TestName} PRIVATE
			/constexpr:steps4294967296
			/constexpr:depth1024
			/constexpr:backtrace256
		)
	endif()

	add_test(NAME ${TestName} COMMAND $<TARGET_FILE:${TestName}> ${ARGN})
endfunction()