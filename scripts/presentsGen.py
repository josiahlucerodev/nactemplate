from typing import List
import itertools
import json

class Option:
    name: str
    body: str
    suboptions: List[any]

    def __init__(self, name, body, suboptions):
        self.name = name
        self.body = body 
        self.suboptions = suboptions

    @classmethod
    def with_body(cls, name, body):
        return cls(name, body, [])

    @classmethod
    def with_suboptions(cls, name, suboptions):
        return cls(name, None, suboptions)

class ConfigGroup:
    name: str 
    options: List[Option]

    def __init__(self, name, options):
        self.name = name
        self.options = options
        

# platform-arch-compiler-type 
s = ",\n"
ls = ","

dir_location = """
    "binaryDir": "${sourceDir}/out/build/${presetName}",
    "installDir": "${sourceDir}/out/install/${presetName}" """

generator = '"generator": "Ninja"' 

windows = """
    "condition": {
        "type": "equals",
        "lhs": "${hostSystemName}",
        "rhs": "Windows"
    } """

windows_msvc = windows + ls + """
    "cacheVariables": {
        "CMAKE_C_COMPILER": "cl.exe",
        "CMAKE_CXX_COMPILER": "cl.exe",
        "CMAKE_BUILD_TYPE": "Debug"
    },
    "environment": {
        "CC": "cl.exe",
        "CXX": "cl.exe"
    } """

windows_clang = windows + ls + """
    "cacheVariables": {
        "CMAKE_C_COMPILER": "clang-cl",
        "CMAKE_CXX_COMPILER": "clang-cl"
    },
    "environment": {
        "CC": "clang-cl",
        "CXX": "clang-cl"
    } """

arch_x64 = """
    "architecture": {
        "value": "x64",
        "strategy": "external"
    } """

windows_x64_default = Option.with_body("windows-x64-default", dir_location + ls + generator + ls + arch_x64 + ls + windows)
windows_x64_msvc = Option.with_body("windows-x64-msvc", dir_location + ls + generator + ls + arch_x64 + ls + windows_msvc)
windows_x64_clang = Option.with_body("windows-x64-clang", dir_location + ls + generator + ls + arch_x64 + ls + windows_clang)

linux = """
    "condition": {
        "type": "equals",
        "lhs": "${hostSystemName}",
        "rhs": "Linux"
    },
    "vendor": {
        "microsoft.com/VisualStudioSettings/CMake/1.0": {
            "hostOS": [ "Linux" ]
        },
        "microsoft.com/VisualStudioRemoteSettings/CMake/1.0": {
            "sourceDir": "$env{HOME}/.vs/$ms{projectDirName}"
        }
    } """ 

linux_x86 = Option.with_body("linux-x64", dir_location + ls + generator + ls + arch_x64 + ls + linux)

web_wasm =  Option.with_body("web-wasm", dir_location + ls + generator + ls + 
    """
        "toolchainFile": "$env{EMSDK}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake",
        "vendor": {
            "microsoft.com/VisualStudioSettings/CMake/1.0": {
                "intelliSenseMode": "windows-clang-x64"
            },
            "condition": {
                "type": "matches",
                "string": "$env{EMSDK}",
                "regex": "emsdk"
            } 
        }"""
)

# build 
debug = Option.with_body("debug", 
     '"cacheVariables": { "CMAKE_BUILD_TYPE": "Debug" }'
)
release = Option.with_body("release", 
    '"cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }'
)

# Option
warnings = Option.with_body("warnings", 
    '"cacheVariables": { "NACTEMPLATE_WARNINGS": "TRUE" }'
)
profile = Option.with_body("profile", 
    '"cacheVariables": { "NACTEMPLATE_PROFILE": "TRUE" }'
)
ipo = Option.with_body("ipo", 
    '"cacheVariables": { "NACTEMPLATE_IPO": "TRUE" }'
)
coverage = Option.with_body("coverage", 
    '"cacheVariables": { "NACTEMPLATE_COVERAGE": "TRUE" }'
)
fuzz = Option.with_body("fuzz", 
    '"cacheVariables": { "NACTEMPLATE_FUZZ": "TRUE" }'
)
test = Option.with_body("test", 
    '"cacheVariables": { "NACTEMPLATE_TEST": "TRUE" }'
)
address_sanitizer = Option.with_body("address_sanitizer", 
    '"cacheVariables": { "NACTEMPLATE_ADDRESS_SANITIZER": "TRUE" }'
)
leak_sanitizer = Option.with_body("leak_sanitizer", 
    '"cacheVariables": { "NACTEMPLATE_LEAK_SANITIZER": "TRUE" }'
)
undefined_sanitizer = Option.with_body("undefined_sanitizer", 
    '"cacheVariables": { "NACTEMPLATE_UNDEFINED_SANITIZER": "TRUE" }'
)
thread_sanitizer = Option.with_body("thread_sanitizer", 
    '"cacheVariables": { "NACTEMPLATE_THREAD_SANITIZER": "TRUE" }'
)
memory_sanitizer = Option.with_body("memory_sanitizer", 
    '"cacheVariables": { "NACTEMPLATE_MEMORY_SANITIZER": "TRUE" }'
)

prototype = Option.with_suboptions("prototype", [test, coverage])
testing = Option.with_suboptions("testing", [test, fuzz, coverage, profile, warnings])
optimized = Option.with_suboptions("optimized", [warnings, ipo])

configGroups: List[ConfigGroup] = [
    ConfigGroup("platform", [windows_x64_default, windows_x64_msvc, windows_x64_clang, linux_x86, web_wasm]), 
    ConfigGroup("build", [debug, release]),
    ConfigGroup("type", [prototype, testing, optimized])
]

options: List[Option] = [
    warnings,
    profile,
    ipo,
    coverage,
    fuzz,
    test,
    address_sanitizer,
    leak_sanitizer,
    undefined_sanitizer,
    thread_sanitizer,
    memory_sanitizer,
]

def begin_config_preset(name: str, hidden: bool):
    return """{
            "name": \"""" + name + """\",
            "hidden": """ + ("true" if hidden else "false")
def end_config_preset():
    return "\n}"

def add_inherited_options(options: List[Option]):
    result: str = '"inherits": ['
    optionsNames: List[str] = []
    for option in options:
        optionsNames.append('"' + option.name + '"')
    result += ", ".join(optionsNames)
    return result + "]"

def add_options(options: List[Option]):
    optionsBodies: List[str] = []
    for option in options:
        optionsBody: str = begin_config_preset(option.name, True)
        if option.body:
            optionsBody += s + option.body
        elif option.suboptions:
            optionsBody += s + add_inherited_options(option.suboptions)          
        optionsBody += end_config_preset()
        optionsBodies.append(optionsBody)
    return s.join(optionsBodies)

def add_config_groups_options(configGroups: List[ConfigGroup]):
    optionsBodys: List[str] = []
    for configGroup in configGroups:
        optionsBodys.append(add_options(configGroup.options))
    return s.join(optionsBodys)

            
def add_config_groups(configGroups: List[ConfigGroup]):
    configBodies: List[str] = []
    configsOptions: List[List[Option]] = [configGroup.options for configGroup in configGroups]
    for options in itertools.product(*configsOptions):
        optionsNames: List[str] = []
        for option in options:
            optionsNames.append(option.name)
        name: str = "-".join(optionsNames)
         
        configBody: str = begin_config_preset(name, False)
        configBody += s + add_inherited_options(options)
        configBody += end_config_preset()
        configBodies.append(configBody)

    return s.join(configBodies)

def write_to_file(path: str, text: str):
    with open(path, "w", encoding="ascii", errors="ignore") as f:
        f.write(text)

def fix_indention(string: str):
    try:
        return json.dumps(json.loads(string), indent=4, ensure_ascii=True)
    except json.JSONDecodeError as e:
        return f"Invalid Gen: {e}"

def gen_configs_json():
    configs: List[str] = []
    configs.append(add_options(options))
    configs.append(add_config_groups_options(configGroups))
    configs.append(add_config_groups(configGroups))
    return s.join(configs)

def gen_config_presents_json():
    result: str = """{
        "version": 4,
        "configurePresets": [
        """
    result += gen_configs_json()
    result += "\n]\n}\n"
    return result.replace("\n\n", "\n")

def main():
    configPresentsJson: str = gen_config_presents_json()
    configPresentsJson = fix_indention(configPresentsJson)
    write_to_file("../presents.json", configPresentsJson)

if __name__ == '__main__':
    main()