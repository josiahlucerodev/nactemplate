# Settings File Format
```
{
	"projects": [
		{
			"name": "",
			"srcDirs": [""],
			"excludeDirs": [],
			"excludeFiles": [],
			"moduleOutput": "",
			"srcListOutput": "",
			"copyFiles": [],
			"allFileName": "",
			"cppHeaderExts": ["", ...],
			"cppSourceExts": ["", ...],
			"cppModuleInterfaceExt": "",
			"cppModuleImplementationExt": ""
		}
    ]
}
```

## Default Template

{
	"projects": [
		{
			"name": "<project_name>",
			"srcDirs": [<project_name>/<project_name>"],
			"excludeDirs": [],
			"excludeFiles": [],
			"moduleOutput": "<project_name>/modules",
			"srcListOutput": "<project_name>/CMakeSources.cmake",
			"copyFiles": [],
			"allFileName": "all",
			"cppHeaderExts": ["hpp", "h"],
			"cppSourceExts": ["cpp"],
			"cppModuleInterfaceExt": "ixx",
			"cppModuleImplementationExt": "cppm"
		},
    ]
}

# Standard Command
If nactemplate is apart of externals folder the standard command to run sourceGen from project root is as follows:
```
python externals/nactemplate/scripts/sourcesGen.py
```