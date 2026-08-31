function(enable_profiling
	project_name) 
	
	if(MSVC)
		target_compile_options(${project_name} PUBLIC /Zi)
		target_link_options(${project_name} PUBLIC /DEBUG)
		target_link_options(${project_name} PUBLIC /OPT:REF)
		target_link_options(${project_name} PUBLIC /OPT:ICF)
		target_link_options(${project_name} PUBLIC /PROFILE)
		set_target_properties(${project_name} PROPERTIES LINK_INCREMENTAL OFF)
		set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /INCREMENTAL:NO")
	else()
		message("profiling unavailable")
	endif()

endfunction()