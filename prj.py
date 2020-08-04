#!/usr/bin/python
'''
UE4 project tools
'''

import argparse, os, sys, time, winreg, json, platform, subprocess, glob, datetime, shutil, fnmatch
import zipfile, py_compile

class UE4:
    '''Utility class for a particular installed version of the Unreal Engine'''
    def __init__(self, version):
        self.version = version # e.g. '4.16'
        self.root = self._GetUnrealDir()
        self.editorPath = self._GetUnrealEditorPath()

    def _GetUnrealDir(self):
        '''Returns the full path to the install directory'''
        # Check the newest way we know how first
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Epic Games\Unreal Engine\Builds') as h:
                dirName, regType = winreg.QueryValueEx(h, self.version)
        except FileNotFoundError:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\EpicGames\Unreal Engine\%s' % self.version) as h:
                    dirName, regType = winreg.QueryValueEx(h, 'InstalledDirectory')
            except FileNotFoundError:
                # Try a different approach - the above worked originally, then broke with 4.15, but appears fixed (even
                # for older versions) in 4.16
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\EpicGames\Unreal Engine') as h:
                        rootDirName, regType = winreg.QueryValueEx(h, 'INSTALLDIR')
                        dirName = os.path.join(rootDirName, self.version)
                        if not os.path.isdir(dirName):
                            dirName = os.path.join(rootDirName, 'UE_%s' % self.version)
                            assert os.path.isdir(dirName)
                except FileNotFoundError:
                    dirName = r'c:\Program Files\Epic Games\UE_%s' % self.version
        return dirName

    def _GetUnrealEditorPath(self):
        '''Returns the full path to the UE4Editor executable, asserting that it exists first'''
        assert platform.system().lower().strip() == 'windows', 'Only Windows support has been implemented, sorry'
        plat = 'Win64' if '64' in platform.architecture()[0] else 'Win32'
        exe = os.path.join(self.root, 'Engine', 'Binaries', plat, 'UE4Editor.exe')
        assert os.path.exists(exe)
        return exe

    def GetRegistryCommand(self, cmd, prjPath):
        '''Reads the Windows Registry to get the command string for the given command. cmd is one of 'open', 'run', 'rungenprog'.'''
        assert cmd in ['open', 'run', 'rungenproj']
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'Unreal.ProjectFile\shell\%s\command' % cmd) as h:
            cmd = winreg.QueryValue(h, None)
            assert '%1' in cmd, cmd
            return cmd.replace('%1', os.path.abspath(prjPath))

class UE4Project:
    '''Utility class for doing stuff with a UE4 project / project directory'''
    def __init__(self, dirName):
        # Make sure there is a single project file in the given directory
        self.dir = os.path.abspath(dirName)
        assert os.path.isdir(dirName)
        prjFiles = glob.glob(os.path.join(dirName, '*.uproject'))
        assert prjFiles, 'ERROR: no Unreal Editor project files found in ' + dirName
        assert len(prjFiles) == 1, 'ERROR: multiple Unreal Editor project files found in' + dirName
        self.path = os.path.abspath(prjFiles[0])

        with open(self.path) as f:
            self.settings = json.loads(f.read())

        self.engine = UE4(self.engineVer)

    @property
    def name(self):
        return os.path.basename(self.path).split('.')[0]

    @property
    def engineVer(self):
        '''returns what version of UE4 this project is configured to use'''
        return self.settings['EngineAssociation']

    def GenVSFiles(self):
        '''[re]generates Visual Studio project files'''
        cmd = self.engine.GetRegistryCommand('rungenproj', self.path)
        assert not subprocess.run(cmd).returncode, cmd

    def GetMaps(self):
        '''Scans the UE4 project and returns a dictionary of mapName --> game path to that map'''
        maps = {}
        for dirName, subdirs, filenames in os.walk(self.dir):
            if '\\Saved\\' in dirName:
                continue
            for filename in filenames:
                if filename.endswith('.umap'):
                    mapName = filename.split('.', 1)[0]
                    mapPath = dirName[len(self.dir):].replace('\\', '/').replace('/Content', '/Game') + '/' + mapName
                    maps[mapName] = mapPath
        return maps

def _IncVersionNumber(filename):
    '''Updates a version number in a version file. Also returns the new version'''
    # bump version number
    today = datetime.date.today().strftime('%Y%m%d')
    with open(filename) as f:
        oldVer = [x for x in f.read().split() if x][-1][1:-1]
    if oldVer.startswith(today):
        buildNum = int(oldVer[-2:]) + 1
    else:
        buildNum = 0
    newVer = '%s%02d' % (today, buildNum)
    with open(filename, 'wt') as f:
        f.write("version = '%s'\n" % newVer)
    return newVer

def GenPYCZip(rootDir, zipFilename, excludeFiles=None, excludeDirs=None):
    '''Walks a directory tree starting at rootDir, compiling all .py files it finds and storing their .pyc
    files in the given zip filename.'''
    excludeFiles = excludeFiles or []
    excludeDirs = excludeDirs or []
    destDir = os.path.dirname(os.path.abspath(zipFilename))
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    rootDir = os.path.abspath(os.path.expanduser(rootDir))
    print('Creating', zipFilename)
    with zipfile.ZipFile(zipFilename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirName, subdirs, filenames in os.walk(rootDir):
            subdirs[:] = [x for x in subdirs if x not in excludeDirs]
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                if filename in excludeFiles:
                    continue
                filename = os.path.join(dirName, filename)
                destName = filename[len(rootDir)+1:]
                print(' ', filename, '-->', destName)
                pycName = filename + 'c'
                py_compile.compile(filename, cfile=pycName, optimize=2)
                with open(pycName, 'rb') as f:
                    pyc = f.read()
                os.remove(pycName)
                with zf.open(destName + 'c', 'w') as f:
                    f.write(pyc)

def BuildModus(buildRoot, newVer, isRelease, clean, buildConfig):
    prj = UE4Project(os.getcwd())
    os.environ['DEVUEPY_IS_BUILDING'] = '1' # see Scripts/common.py

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    if clean:
        buildFlags = ['-clean', '-compile']
        # gotta nuke DLLs too
        for dirName, subdirs, filenames in os.walk(THIS_DIR):
            for filename in filenames:
                if fnmatch.fnmatch(filename, 'UE4Editor-*.dll'):
                    full = os.path.join(dirName, filename)
                    print('Deleting', full)
                    os.remove(full)

        # Some dude on the interwebs (https://blog.mi.hdm-stuttgart.de/index.php/2017/02/11/uat-automation/) says we have to
        # next use a different build command and, since I can't get RunUAT to build our DLLs, I guess he's right!
        bat = os.path.join(prj.engine.root, 'Engine', 'Build', 'BatchFiles', 'Build.bat')
        assert os.path.exists(bat), bat
        args = [bat, prj.name, 'Win64', buildConfig, prj.path, '-WaitMutex']
        ret = subprocess.run(args).returncode
        assert not ret
    else:
        buildFlags = ['-nocompile', '-nocleanstage']

    if 1:
        uat = os.path.join(prj.engine.root, 'Engine', 'Build', 'BatchFiles', 'RunUAT.bat')
        assert os.path.exists(uat), uat

        args = [uat]
        # removed: -iterativecooking -iterate -fastcook
        args.extend('BuildCookRun -CrashReporter -utf8output -build -targetplatform=Win64 -platform=Win64 -NoP4'.split())
        args.extend(buildFlags)
        args.append('-CreateReleaseVersion=%s' % newVer)
        args.append('-verbose -encryptinifiles')
        args.extend('-cook -distribution -package -prereqs -allmaps -installed'.split())
        args.append('-clientconfig=' + buildConfig)
        #if isRelease:
        #    args.append('-nocompileeditor')
        args.append('-pak') # make this optional?
        args.append('-stage')
        args.append('-stagingdirectory="%s"' % buildRoot)
        args.append('-ScriptsForProject="%s"' % prj.path)
        args.append('-project="%s"' % prj.path)
        start = time.time()
        ret = subprocess.run(args).returncode
        print('EXIT CODE:', ret, 'dur:', time.time() - start)
        assert not ret

    # Clean up some weird files
    for item in ['Manifest_DebugFiles_Win64.txt', 'Manifest_NonUFSFiles_Win64.txt', 'FileOpenOrder',
                r'Engine\Binaries\Win64\CrashReportClient.pdb']:
        fullPath = os.path.join(buildRoot, 'WindowsNoEditor', item)
        if os.path.isdir(fullPath):
            print('Cleaning up', fullPath)
            shutil.rmtree(fullPath)
        elif os.path.isfile(fullPath):
            print('Cleaning up', fullPath)
            os.remove(fullPath)

    # Copy the Python binaries
    print('Copying Python files')
    srcDir = os.path.join(prj.dir, 'Plugins', 'uepy', 'python')
    destDir = os.path.join(buildRoot, 'WindowsNoEditor', 'dev_uepy', 'Binaries', 'Win64')
    for filename in os.listdir(srcDir):
        srcPath = os.path.join(srcDir, filename)
        if os.path.isdir(srcPath) or srcPath.endswith('.exe'): # we don't need these
            continue
        destPath = os.path.join(destDir, filename)
        print(' ', srcPath, '-->', destPath)
        shutil.copyfile(srcPath, destPath)

    # Copy the python scripts - fm.zip is common stuff for UE4+Python, modus.zip holds modus-specific stuff
    #destRoot = os.path.join(buildRoot, 'WindowsNoEditor', 'modus', 'Content', 'Scripts')
    #GenPYCZip(os.path.join(prj.dir, 'Plugins', 'UnrealEnginePython', 'Content', 'Scripts'), os.path.join(destRoot, 'fm.zip'))
    #GenPYCZip(os.path.join(prj.dir, 'Content', 'Scripts'), os.path.join(destRoot, 'modus.zip'), ['ue_site.py'], ['ObjectLibraries'])

    # Manually copy over stuff that isn't included in the zips - we currently don't put ObjectLibraries into the zip, because
    # the dynamic class loader doesn't know how to find them inside the zip, but we do at least ship a pyc instead of a py
    # (for a modicum of security through obscurity)
    if 0:
        shutil.copyfile(os.path.join(prj.dir, 'Content', 'Scripts', 'ue_site.py'), os.path.join(destRoot, 'ue_site.py'))
        olSrcRoot = os.path.join(prj.dir, 'Content', 'Scripts', 'ObjectLibraries')
        olDestRoot = os.path.join(destRoot, 'ObjectLibraries')
        for dirName, subdirs, filenames in os.walk(olSrcRoot):
            for filename in filenames:
                srcName = os.path.join(dirName, filename)
                if '__pycache__' in srcName or 'DO_NOT_PUT' in srcName:
                    continue
                destName = os.path.join(olDestRoot, srcName[len(olSrcRoot)+1:])
                if not os.path.exists(os.path.dirname(destName)):
                    os.makedirs(os.path.dirname(destName))
                print(srcName, '-->', destName)

                # We copy most everything (in case there are auxiliary files of some sort), but any .py file we compile
                if filename.lower().endswith('.py'):
                    destName += 'c'
                    py_compile.compile(srcName, cfile=destName, optimize=2)
                else:
                    shutil.copy2(srcName, destName)

    os.environ['DEVUEPY_IS_BUILDING'] = '0' # see Scripts/common.py

def CLIBuild():
    clean = False
    buildConfig = 'Shipping'
    isRelease = True
    thisDir = os.path.dirname(os.path.abspath(__file__))
    buildRoot = os.path.join(thisDir, 'Build')
    if not os.path.isdir(buildRoot):
        os.makedirs(buildRoot)
    BuildModus(buildRoot, '00000000', isRelease, clean, buildConfig)

def CLIRun(args, leftovers):
    Run(leftovers, not args.nowait)

def Run(extraArgs, wait=True):
    '''Runs modus from the command line (but still unpackaged). extraArgs is a list of additional command line
    parameters to pass to modus itself. If wait is False, launch and then disconnect from the process instead
    of waiting for it to terminate.'''

    prj = UE4Project(os.getcwd())
    print('Loaded UE', prj.engineVer, 'project at', prj.path)

    # Fix up args
    if '-game' not in extraArgs and '-server' not in extraArgs:
        extraArgs.append('-game')
    if '-log' not in extraArgs:
        extraArgs.append('-log')

    # If any maps were given by just their name, replace them with the full game path for that map
    maps = prj.GetMaps()
    for i, arg in enumerate(extraArgs):
        parts = arg.split('?', 1)
        mapExtra = ''
        if len(parts) > 1:
            arg, mapExtra = parts[:2]
            if mapExtra:
                mapExtra = '?' + mapExtra

        if arg in maps:
            extraArgs[i] = maps[arg] + mapExtra

    cmd = '"%s" "%s"' % (prj.engine.editorPath, prj.path) + ' ' + ' '.join(extraArgs)
    s = subprocess.Popen(cmd)
    if wait:
        s.wait()

def NukeBinaries(args):
    '''Clean all the Binaries and Intermediate directories in the project'''
    folders = [
        'Binaries',
        'Intermediate'
    ]
    for root, dirs, files in os.walk('Plugins'):
        if root.split(os.sep)[-1] in ('Binaries', 'Intermediate'):
            folders.append(root)

    for folder in folders: 
        if os.path.isdir(folder):
            print(f'deleting {folder}')
            shutil.rmtree(folder)

def CLINukeDLLs(args):
    '''Removes all DLLs, forcing relink (and recompile) as needed'''
    for dirName, subDirs, filenames in os.walk('.'):
        for filename in filenames:
            low = filename.lower()
            if low.startswith('ue4') and low.endswith('.dll'):
                full = os.path.abspath(os.path.join(dirName, filename))
                print('Erasing', full)
                os.remove(full)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UE4 Project Tool')
    subs = parser.add_subparsers(help='sub-command help')

    run = subs.add_parser('run', help='Run prj from command line')
    run.add_argument('--nowait', action='store_true', help='Disconnect from the launched process instead of waiting for it to terminate')
    #run.add_argument('--instance', help='Instance nickname. Used for running multiple instances on the same machine.')
    run.set_defaults(func=CLIRun)

    build = subs.add_parser('build', help='Build stuffs')
    build.add_argument('-c', '--configuration', default='Shipping', help='Override the build configuration: Development, Shipping, Test')
    build.add_argument('--skip-clean', action='store_true', help='Do not clean up stuff before building')
    build.add_argument('--skip-crashreporter', action='store_true', help='FOR DEBUGGING, skip building CrashReporter.exe')
    build.add_argument('--skip-modus', action='store_true', help='FOR DEBUGGING, skip building Modus')
    build.add_argument('--skip-launcher', action='store_true', help='FOR DEBUGGING, skip building the 2D launcher')
    build.add_argument('--skip-installer', action='store_true', help='FOR DEBUGGING, skip building the installer')
    build.set_defaults(func=CLIBuild)

    nukeb = subs.add_parser('nukeb', help='Nuke Binaries and Intermediate folders')
    nukeb.set_defaults(func=NukeBinaries)

    nukedlls = subs.add_parser('nuked', help='Nuke all DLLs (like nukeb, but not quite as heavy-handed')
    nukedlls.set_defaults(func=CLINukeDLLs)

    args, leftovers = parser.parse_known_args()
    if 'func' in args:
        if args.func == CLIRun:
            args.func(args, leftovers) # hackery to make e.g. prj.py -vr work like older launcher.py -vr
        else:
            args.func(args)
    else:
        parser.print_help()

