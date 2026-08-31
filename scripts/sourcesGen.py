import os
from typing import List
from typing import Optional
from typing import Tuple
from pathlib import Path
import json
import sys
from typing import Any

def load_file_content(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def report_error(filepath: str, error: str, section: str = ""):
    if section:
        print(filepath + ": " + error, "in section {", section, "}")
    else:
        print(filepath + ": " + error)

def write_to_file(filepath: str, content: str, emcod: str = 'utf-8') -> bool:
    try:
        ocontent = load_file_content(filepath)
        if content == ocontent:
            return True
    except:
        pass

    try:
        with open(filepath, 'w', encoding=emcod) as file:
            file.write(content)
            return True
    except Exception as e:
        report_error(filepath, f"failed to write content to file {e}")
        return False

def ends_with_any(s: str, suffixList: List[str]) -> bool:
    return s.endswith(tuple(suffixList))

def remove_extension(filename: str) -> str:
    base, _ = os.path.splitext(filename)
    return base

def add_extension(filename: str, ext: str) -> str:
    if not ext.startswith("."):
        ext = "." + ext
    if not filename.endswith(ext):
        filename += ext
    return filename

class ProjectSettings:
    def __init__(self):
        self.name: str
        self.srcDirs: List[str]
        self.excludeDirs: List[str]
        self.excludeFiles: List[str]
        self.copyFiles: List[str]
        self.moduleOutput: str
        self.srcListOutput: Optional[str]
        self.allFileName: str

        self.cppHeaderExts: List[str]
        self.cppSourceExts: List[str]
        self.cppModuleInterfaceExt: str
        self.cppModuleImplementationExt: str
        return

class File:
    def __init__(self, name: str, filepath: Path, parent: 'Dir'):
        self.name = name
        self.filepath = filepath
        self.parent = parent
        self.isHeader = False

class Dir:
    def __init__(self, name: str, filepath: Path):
        self.name = name
        self.filepath = filepath
        self.parent: Optional['Dir'] = None
        self.dirs: List['Dir'] = []
        self.files: List[File] = []
        self.headers: List[File] = []
        self.modules: List[str] = []
        self.copyFiles: List[str] = [] 
        self.allFile: Optional[File]

def get_module_name(file: File) -> str:
    moduleSections: List[str] = []
    moduleSections.append(remove_extension(file.name))
    dir = file.parent
    while dir is not None:
        moduleSections.append(dir.name)
        dir = dir.parent
    moduleSections.reverse()
    return ".".join(moduleSections)

def process_includes(file: File, content: str, projectSettings: ProjectSettings) -> str:
    lines = content.splitlines()
    filepath = file.filepath.as_posix()
    newLines: List[str] = []
    error = ""
    isImpl = ends_with_any(file.name, projectSettings.cppSourceExts + [projectSettings.cppModuleImplementationExt])
    
    def module_line(moduleSections: List[str], line: str, isInterfaceHint: bool) -> str:
        module = ".".join(moduleSections)
        if isInterfaceHint:
            return "module " + module + ";\n"

        if isImpl or line.find("//@no_export") != -1:
            module = "import " + module + ";"
        else:
            module = "export import " + module + ";"
        return module

    isInterfaceHint = False
    for line in lines:
        if line.find("//@interface") != -1:
            isInterfaceHint = True
            newLines.append("//@interface")
            continue
        if line.find("#include <") != -1:
            if line.find(">") == -1:
                report_error(filepath, "expected > at end of include path", line)
                return error
            path = line[line.find("#include <") + len("#include <") : line.find(">")]
            pathSections: List[str] = path.split("/"); 
            if pathSections:
                pathSections[-1] = remove_extension(pathSections[-1])
            for pathSection in pathSections:
                if pathSection == "..":
                    return error
            newLines.append(module_line(pathSections, line, isInterfaceHint))
            isInterfaceHint = False
        elif line.find("#include \"") != -1:
            if line.find("\"") == -1:
                report_error(filepath, "expected \" at end of include path", line)
                return error
            
            path = line[line.find("#include \"") + len("#include \"") :line.rfind("\"")]
            pathSections: List[str] = path.split("/"); 
            
            activeDir = file.parent
            if len(pathSections) == 0:
                report_error(filepath, "expected file path in include path", line)
                return error

            for pathSection in pathSections[:-1]:
                if pathSection == "..":
                    if activeDir.parent is not None:
                        activeDir = activeDir.parent
                    else:
                        report_error(filepath, "include has to many .. going out of search context", line)
                        return error
                else:
                    nextDir: Optional[Dir] = next((d for d in activeDir.dirs if d.name == pathSection), None)
                    if nextDir is not None:
                        activeDir = nextDir
                    else:
                        report_error(filepath, "dir as pathsection {" + pathSection + "} in include does not exist ", line)
                        return error
            
            fileSection = pathSections[-1]
            includeFile: Optional[File] = next((f for f in activeDir.files if f.name == fileSection), None)
            if includeFile is not None:
                moduleSections: List[str] = []
                moduleSections.append(remove_extension(includeFile.name))
                
                dir: Optional[Dir] = includeFile.parent
                while dir is not None:
                    moduleSections.append(dir.name)
                    dir = dir.parent

                moduleSections.reverse()

                newLines.append(module_line(moduleSections, line, isInterfaceHint))
                isInterfaceHint = False
            else:
                report_error(filepath, "file in include path does not exist", line)
                return error
                         
        elif line.find("#include") != -1:
            report_error(filepath, "there is a #include of unknown format", line)
            return error
        else:
            newLines.append(line)
    return "\n".join(newLines)

def get_module_path(dir: Dir) -> str:
    moduleSection: List[str] = []
    adir: Optional[Dir] = dir 
    while adir is not None:
        moduleSection.append(dir.name)
        adir = adir.parent
    return ".".join(moduleSection)
from typing import List, Tuple, Optional

class FileSection:
    def __init__(self, isMatch: bool, content: str) -> None:
        self.isMatch = isMatch
        self.content = content

def split_file(file: File, begin: str, end: str) -> Optional[Tuple[str, List[FileSection]]]:
    error = None
    filepath = file.filepath.as_posix()
    if not os.path.exists(filepath):
        report_error(filepath, "src does not exist")
        return error


    content = load_file_content(filepath)
    sections: List[FileSection] = []
    rcontent = content

    while rcontent:
        bindex = rcontent.find(begin)
        eindex = rcontent.find(end)

        if bindex != -1 or eindex != -1:
            if bindex == -1:
                report_error(filepath, "expected matching " + end + " to be after " + begin)
                return error
            if eindex == -1:
                report_error(filepath, "expected matching " + begin + " to be before " + end) 
                return error
            if not bindex < eindex:
                report_error(filepath, "expected matching " + begin + " to be before " + end) 
                return error
            
            section = rcontent[ : bindex]
            msection = rcontent[bindex + len(begin) : eindex]
            
            if section:
                sections.append(FileSection(False, section))
            if msection:
                sections.append(FileSection(True, msection))
            rcontent = rcontent[eindex + len(end):]
        else:
            sections.append(FileSection(False, rcontent))
            rcontent = ""
    return (content, sections)

def process_all_file_header(file: File) -> str:
    error = ""
    sectionsData = split_file(file, "//@being_auto_subdir_list", "//@end_auto_subdir_list")
    if sectionsData is None:
        return error
    _, sections = sectionsData

    def gen_header_content(headers: List[File], subname: str) -> str:
        if headers:
            headerContent = "\n//" + subname + "\n"
            for header in headers:
                headerContent += "#include \"" + os.path.relpath(header.filepath, file.filepath)[3:] + "\"\n" 
            return headerContent
        else:
            return ""

    for section in sections:
        if not section.isMatch:
            continue
        
        allHeaders: List[File] = []
        for dir in file.parent.dirs:
            if dir.allFile is not None:
                allHeaders.append(dir.allFile) 
        srcListContent = ""
        srcListContent += "//@being_auto_subdir_list"
        srcListContent += gen_header_content(allHeaders, "subdirs")
        srcListContent += gen_header_content(file.parent.headers, "subfiles")
        srcListContent += "//@end_auto_subdir_list"
        section.content = srcListContent
    
    file.parent.headers.append(file)

    ncontent = ""
    for section in sections:
        ncontent += section.content
    return ncontent

def process_all_file_module(file: File) -> str:
    error = ""
    sectionsData = split_file(file, "//@being_auto_subdir_list", "//@end_auto_subdir_list")
    if sectionsData is None:
        return error
    _, sections = sectionsData
    
    def gen_module_content(modules: List[str], subname: str) -> str:
        if modules:
            moduleContent = "//" + subname + "\n"
            for module in modules:
                moduleContent += "export import " + module + ";\n" 
            return moduleContent
        else:
            return ""

    for section in sections:
        if not section.isMatch:
            continue

        allModules: List[str] = []
        for dir in file.parent.dirs:
            if dir.allFile is not None:
                allModules.append(get_module_name(dir.allFile))

        srcListContent = ""
        srcListContent += gen_module_content(allModules, "subdirs")
        srcListContent += gen_module_content(file.parent.modules, "subfiles")
        section.content = srcListContent
    
    ncontent = ""
    for section in sections:
        ncontent += section.content

        
    moduleName = get_module_name(file)
    ncontent = ncontent.replace("#pragma once", "export module " + moduleName + ";")
    ncontent = ncontent.replace("//@export", "export")
    file.parent.modules.append(moduleName)
    return ncontent

def insert_at(s: str, index: int, insert_str: str):
    return s[:index] + insert_str + s[index:]

def process_file(file: File, projectSettings: ProjectSettings) -> str:
    moduleName = get_module_name(file)
    error = ""

    if ends_with_any(file.name, projectSettings.cppHeaderExts):
        file.parent.headers.append(file)

    error = ""
    sectionsData = split_file(file, "//@begin_non_modules", "//@end_non_modules")
    if sectionsData is None:
        return error
    content, sections = sectionsData
    
    nonModuleContent = ""
    ncontent = ""
    for section in sections:
        if section.isMatch:
            nonModuleContent += section.content
        else:
            pcontent = process_includes(file, section.content, projectSettings)
            if not pcontent:
                return error
            ncontent += pcontent

    isHeader = content.find("#pragma once") != -1
    isInterface = content.find("//@interface") != -1
    isFileNotModule = content.find("//@file_not_module") != -1

    fcontent = ""
    if isHeader:
        moduleHeader = ""
        moduleHeader += "module;\n"
        moduleHeader += nonModuleContent + "\n"
        moduleHeader += "export module " + moduleName + ";\n\n"
        file.parent.modules.append(moduleName)
        fcontent = moduleHeader + ncontent.replace("#pragma once", "").lstrip()
    elif isInterface:
        moduleHeader = ""
        moduleHeader += "module;\n"
        moduleHeader += nonModuleContent + "\n"
        fcontent = insert_at(ncontent, ncontent.find("module"), moduleHeader).replace("//@interface", "").lstrip()
    elif isFileNotModule:
        fcontent = (nonModuleContent + ncontent).lstrip()
    else:
        report_error(file.filepath.as_posix(), "unknown file type")
        return error
    
    fcontent = fcontent.replace("//@export", "export")
    return fcontent
    
    
def output_file(file: File, outputPath: str, content: str, projectSettings: ProjectSettings):
    fileOutputPath = outputPath; 
    noExtFileName = remove_extension(file.name)
    if ends_with_any(file.name, projectSettings.cppHeaderExts):
        fileOutputPath = os.path.join(fileOutputPath, add_extension(noExtFileName, projectSettings.cppModuleInterfaceExt))
    else:
        fileOutputPath = os.path.join(fileOutputPath, add_extension(noExtFileName, projectSettings.cppModuleImplementationExt))
    write_to_file(fileOutputPath, content)


def process_dir(rdir: Dir, projectSettings: ProjectSettings, outputPath: str):
    outputPath = os.path.join(outputPath, rdir.name)

    if rdir.dirs or rdir.files or rdir.copyFiles:
        os.makedirs(outputPath, exist_ok=True)

    for copyfile in rdir.copyFiles:
        content = load_file_content(copyfile)
        dstPath = os.path.join(outputPath, Path(copyfile).name)
        write_to_file(dstPath, content)

    for dir in rdir.dirs:
        process_dir(dir, projectSettings, outputPath)

    allFile: Optional[File] = None
    for file in rdir.files:
        if remove_extension(file.name) == projectSettings.allFileName:
            allFile = file
            continue
        content = process_file(file, projectSettings)
        output_file(file, outputPath, content, projectSettings)

    rdir.allFile = None
    if allFile is not None:
        moduleContent = process_all_file_module(allFile)
        output_file(allFile, outputPath, moduleContent, projectSettings)
        rdir.allFile = allFile

        headerContent = process_all_file_header(allFile)
        if headerContent: 
            write_to_file(allFile.filepath.as_posix(), headerContent)
        else:
            report_error(allFile.filepath.as_posix(), "failed to proccess header", "")
    
def get_dir(dirpath: Path, fileExt: List[str], projectSettings: ProjectSettings, parent: Optional['Dir'] = None) -> Optional[Dir]:
    error = None
    if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
        report_error(dirpath._str, "dir does not exist")
        return error
    
    rdir = Dir(dirpath.name, dirpath)
    rdir.parent = parent
    dirs = [p for p in dirpath.iterdir() if p.is_dir()]
    files = [p for p in dirpath.iterdir() if p.is_file()]

    for dir in dirs:
        if dir.name in projectSettings.excludeDirs:
            continue
        gdir = get_dir(dir, fileExt, projectSettings, rdir)
        if gdir is not None:
            rdir.dirs.append(gdir)

    for file in files:
        if file.name in projectSettings.copyFiles:
            rdir.copyFiles.append(file.as_posix())
            continue

        if file.name in projectSettings.excludeFiles:
            continue

        if not ends_with_any(file.name, fileExt):
            continue 
        rfile = File(file.name, file, rdir)
        rfile.isHeader = ends_with_any(file.name, projectSettings.cppHeaderExts)
        rdir.files.append(rfile)

    return rdir

def get_dir_files(rdir: Dir, fileExts: List[str]) -> List[File]:
    files: List[File] = []
    for dir in rdir.dirs:
        files.extend(get_dir_files(dir, fileExts))
    
    for file in rdir.files:
        if ends_with_any(file.name, fileExts):
            files.append(file)
    
    return files

def covert_files_to_paths(basePath: str, files: List[File]) -> List[str]:
    paths: List[str] = []
    
    for file in files:
        paths.append(os.path.relpath(file.filepath, basePath).replace('\\', '/'))
    return paths

def gen_sources_list(dir: Dir, moduleDir: Dir, srcListOutput: str, projectSettings: ProjectSettings):
    basePath = Path(srcListOutput).parent.as_posix()
    def convert_to_content(varName: str, files: List[File]) -> str:
        content = ""
        if files:
            content = f"set({varName}\n"
            content += "\n".join(covert_files_to_paths(basePath, files))
            content += ")\n\n"
        return content

    cppHeaderFiles = get_dir_files(dir, projectSettings.cppHeaderExts)
    cppSourceFiles = get_dir_files(dir, projectSettings.cppSourceExts)

    cppModuleHeaderFiles = get_dir_files(moduleDir, projectSettings.cppHeaderExts)
    cppModuleSourceFiles = get_dir_files(moduleDir, projectSettings.cppSourceExts)
    cppModuleInterfaceFiles = get_dir_files(moduleDir, [projectSettings.cppModuleInterfaceExt])
    cppModuleImplementationFiles = get_dir_files(moduleDir, [projectSettings.cppModuleImplementationExt])

    srcListContent = ""
    srcListContent += convert_to_content("CPP_HEADER_FILES", cppHeaderFiles)
    srcListContent += convert_to_content("CPP_SOURCE_FILES", cppSourceFiles)
    srcListContent += convert_to_content("CPP_MODULE_HEADER_FILES", cppModuleHeaderFiles)
    srcListContent += convert_to_content("CPP_MODULE_SOURCE_FILES", cppModuleSourceFiles)
    srcListContent += convert_to_content("CPP_MODULE_INTERFACE_FILES", cppModuleInterfaceFiles)
    srcListContent += convert_to_content("CPP_MODULE_IMPLEMENTATION_FILES", cppModuleImplementationFiles)

    write_to_file(srcListOutput, srcListContent, 'ascii')
    return

def process_project(projectSettings: ProjectSettings):
    print("Project:", projectSettings.name)
    for srcDir in projectSettings.srcDirs:
        searchFileExts = projectSettings.cppHeaderExts + projectSettings.cppSourceExts
        dir = get_dir(Path(srcDir), searchFileExts, projectSettings)
        if dir is not None and dir.dirs:
            process_dir(dir, projectSettings, projectSettings.moduleOutput)
            
            if projectSettings.srcListOutput is None:
                continue
            
            searchFileExts.append(projectSettings.cppModuleInterfaceExt)
            searchFileExts.append(projectSettings.cppModuleImplementationExt)
            moduleDir = get_dir(Path(projectSettings.moduleOutput), searchFileExts, projectSettings)

            if moduleDir:
                gen_sources_list(dir, moduleDir, projectSettings.srcListOutput, projectSettings)
            else:
                report_error(projectSettings.moduleOutput, "expected dirs and files in module dir")

def json_read_str_list(jsonElement: Any) -> List[str]:
    items: List[str] = []
    for item in jsonElement:
        items.append(item)
    return items 

def load_projects_settings(projectDir: str) -> Optional[List[ProjectSettings]]:
    error = None

    projectSettingsFile = os.path.join(projectDir, ".nctsettings")
    if not os.path.exists(projectSettingsFile):
        report_error(projectSettingsFile, ".nctsettings settings file does not exist")
        return error
    
    content = load_file_content(projectSettingsFile)
    if not content:
        return error
    
    jsonData = json.loads(content)
    projectSettings: List[ProjectSettings] = []
    for projectData in jsonData["projects"]:
        ps = ProjectSettings()
        ps.name = projectData["name"]
        ps.srcDirs = json_read_str_list(projectData["srcDirs"])
        ps.excludeDirs = json_read_str_list(projectData["excludeDirs"])
        ps.excludeFiles = json_read_str_list(projectData["excludeFiles"])
        ps.copyFiles = json_read_str_list(projectData["copyFiles"])
        ps.moduleOutput = projectData["moduleOutput"]
        ps.srcListOutput = projectData.get("srcListOutput")
        ps.allFileName = projectData["allFileName"]

        ps.cppHeaderExts = json_read_str_list(projectData["cppHeaderExts"])
        ps.cppSourceExts = json_read_str_list(projectData["cppSourceExts"])
        ps.cppModuleInterfaceExt = projectData["cppModuleInterfaceExt"]
        ps.cppModuleImplementationExt = projectData["cppModuleImplementationExt"]
        projectSettings.append(ps)

    return projectSettings

def main():
    projectsDir: str
    if len(sys.argv) < 2:
        projectsDir = os.getcwd()
    else:
        projectsDir = sys.argv[1]
    print(projectsDir)

    if (not os.path.exists(projectsDir)) or (not os.path.isdir(projectsDir)):
        print("expect path " + projectsDir + " to be dir")
    os.chdir(projectsDir)

    projectsSettings = load_projects_settings(projectsDir)
    if projectsSettings is None:
        return

    for projectSettings in projectsSettings:
        process_project(projectSettings)

if __name__ == '__main__':
    main()