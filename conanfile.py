#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class SPDLogSetupConan(ConanFile):
    name = "spdlog_setup"
    version = "master"
    url = "https://github.com/bincrafters/conan-spdlog_setup"
    description = "spdlog setup initialization via file configuration for convenience."

    # Indicates License type of the packaged library
    license = "MIT"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"build_tests": [True, False]}
    default_options = "build_tests=True"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    # Use version ranges for dependencies unless there's a reason not to
    requires = (
        "cpptoml/master@jgsogo/testing",
        "rustfp/master@jgsogo/testing",
        "fmt/[>=4.1.0]@bincrafters/stable",
        "spdlog/[>=0.14.0]@bincrafters/stable",
        "catch2/[>=2.1.0]@bincrafters/stable"
    )

    def source(self):
        source_url = "https://github.com/guangie88/spdlog_setup"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        # Work to remove 'deps' directory (conan will handle them)
        shutil.rmtree(os.path.join(extracted_dir, "deps"))
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"), "add_subdirectory(deps/cpptoml)", "")
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"), "add_subdirectory(deps/rustfp)", "")
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"), "add_subdirectory(deps/spdlog)", "")
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"), "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/deps/fmt>", "")

        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"),
'''
install(DIRECTORY deps/fmt/fmt DESTINATION include
  PATTERN deps/fmt/fmt/*.txt EXCLUDE)
''', "")
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"),
'''
  target_include_directories(spdlog_setup_unit_test
    PRIVATE
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/deps/Catch/include>)
''', "")
        tools.replace_in_file(os.path.join(extracted_dir, "CMakeLists.txt"),
'''
target_link_libraries(spdlog_setup
  INTERFACE
    cpptoml
    rustfp
    spdlog)
''', "")

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)


    def build(self):
        cmake = CMake(self)
        cmake.definitions["SPDLOG_SETUP_INCLUDE_UNIT_TESTS"] = self.options.build_tests
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        if self.options.build_tests:
            # cmake.test()
            pass
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
    
    def package_id(self):
        self.info.header_only()

