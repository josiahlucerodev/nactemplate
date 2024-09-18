function(
	enable_warnings 
	project_name
	ENABLE_WARNINGS_AS_ERRORS
	) 
	#warning_flags

	set(cxx_warning_flags "")
	set(cxx_clang_warning_flags 
			-Wall
			-Wextra
			-Wpedantic
			-Wshadow
			-Wold-style-cast
			-Wcast-align
			-Wunused 
			-Woverloaded-virtual
			-Wconversion
			-Wsign-conversion
			-Wnull-dereference
			-Wdouble-promotion
			-Wformat=2
			-Wimplicit-fallthrough
	)


	if(MSVC)
		set(cxx_warning_flags
			/W4
			/w14242
			/w14254
			/w14263
			/w14265
			/w14287
			/we4289
			/w14296
			/w14311
			/w14545
			/w14546
			/w14547
			/w14549
			/w14555
			/w14640
			/w14826
			/w14928
			/permissive-)

		string(REGEX REPLACE "/W[0-3]" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
		set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}" CACHE STRING "" FORCE)
		string(REGEX REPLACE "/W[0-3]" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
		set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}" CACHE STRING "" FORCE)
	elseif(CMAKE_CXX_COMPILER_ID MATCHES ".*Clang")
		set(cxx_warning_flags
			${cxx_clang_warning_flags}
		)
	elseif(CMAKE_CXX_COMPILER_ID MATCHES ".*GNU")
		set(cxx_warning_flags
			${cxx_clang_warning_flags}
			-Wmisleading-indentation 
			-Wduplicated-cond 
			-Wduplicated-branches
			-Wlogical-op  
			-Wsuggest-override
		)
	else()
		message("nactemplate: unable to enable compiler warnings")
	endif()

	if(${ENABLE_WARNINGS_AS_ERRORS})
		if(MSVC)
			list(APPEND cxx_warning_flags /WX)
		elseif(CMAKE_CXX_COMPILER_ID MATCHES ".*Clang")
		    list(APPEND cxx_warning_flags -Werror)
		elseif(CMAKE_CXX_COMPILER_ID MATCHES ".*GNU")
		    list(APPEND cxx_warning_flags -Werror)
		else()
			message("nactemplate: unable to enable compiler warnings as errors")
		endif()
	endif()

	target_compile_options(${project_name} PRIVATE ${cxx_warning_flags})
endfunction()