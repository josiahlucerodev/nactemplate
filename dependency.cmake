function(test_for_dependency
	dependency_name
	dependency_used)

	if(TARGET ${dependency_name})
		set(${dependency_used} TRUE PARENT_SCOPE)
	else()
		set(${dependency_used} FALSE PARENT_SCOPE)
	endif()

endfunction()

function(add_dependency
	dependency_name) 
	test_for_dependency(${dependency_name} dependency_used)

	if(dependency_used) 
		message(FATEL_ERROR "${dependency_name} is already used")
	endif()
endfunction()
