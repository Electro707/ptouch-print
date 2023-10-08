cmake_minimum_required(VERSION 3.15)

project(ptouch-print C)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")

include(GNUInstallDirs)
set(CMAKE_INSTALL_PREFIX /usr)
set(CMAKE_C_STANDARD 11)

# Configure required dependencies
find_package(Gettext REQUIRED)
find_package(GD REQUIRED)
find_package(Git REQUIRED)
find_package(PkgConfig REQUIRED)
find_package(Intl REQUIRED)
find_package(SWIG REQUIRED)
find_package(PythonLibs REQUIRED)

pkg_check_modules(LIBUSB REQUIRED libusb-1.0)

INCLUDE(${SWIG_USE_FILE})
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})
#INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS "")


add_library(ptouch SHARED)

target_include_directories(ptouch PUBLIC
	${CMAKE_BINARY_DIR}	# HB9HEI - location of generated version.h
	${CMAKE_SOURCE_DIR}/include
	${GD_INCLUDE_DIR}
	${LIBUSB_INCLUDE_DIRS}
	${Intl_INCLUDE_DIRS}
)

target_link_libraries(ptouch PUBLIC
	${GD_LIBRARIES}
	${LIBUSB_LIBRARIES}
	${LIBUSB_LINK_LIBRARIES}
	${Intl_LIBRARIES}
)

target_sources(ptouch PUBLIC
	include/ptouch.h
	include/gettext.h
	src/libptouch.c
)

# Configure project executable
add_executable(${PROJECT_NAME})

target_include_directories(${PROJECT_NAME} PUBLIC
	${CMAKE_BINARY_DIR}	# HB9HEI - location of generated version.h
	${CMAKE_SOURCE_DIR}/include
	${GD_INCLUDE_DIR}
	${LIBUSB_INCLUDE_DIRS}
	${Intl_INCLUDE_DIRS}
)

target_link_libraries(${PROJECT_NAME} PUBLIC
	ptouch
)

# target_link_libraries(${PROJECT_NAME} PRIVATE
# 	${GD_LIBRARIES}
# 	${LIBUSB_LIBRARIES}
# 	${LIBUSB_LINK_LIBRARIES}
# 	${Intl_LIBRARIES}
# )

target_sources(${PROJECT_NAME} PRIVATE
	src/ptouch-print.c
	include/ptouch.h
)

add_dependencies(${PROJECT_NAME}
	git-version
	ptouch
)

target_compile_definitions(${PROJECT_NAME} PUBLIC
	LOCALEDIR="${CMAKE_INSTALL_LOCALEDIR}"
	USING_CMAKE=1
	PACKAGE="ptouch-print"
)

target_compile_options(${PROJECT_NAME} PUBLIC
	-g
	-Wall
	-Wextra
	-Wunused
	-O3
	-fPIC
)

# HB9HEI - custom target that produces version.h	(req. cmake 3.0)
add_custom_target(git-version ALL
	${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/gitversion.cmake
)

# SET_SOURCE_FILES_PROPERTIES(src/ptouchSwig.i PROPERTIES SWIG_FLAGS "-includeall")
SWIG_ADD_LIBRARY(libptouchSwig TYPE MODULE LANGUAGE python OUTFILE_DIR ${CMAKE_CURRENT_BINARY_DIR} OUTPUT_DIR ${CMAKE_SOURCE_DIR}/pyTouch SOURCES
	pyTouch/libptouch.i
	include/ptouch.h
	include/gettext.h
	src/libptouch.c
)
target_link_libraries(libptouchSwig PUBLIC
	${PYTHON_LIBRARIES}
	${GD_LIBRARIES}
	${LIBUSB_LIBRARIES}
	${LIBUSB_LINK_LIBRARIES}
	${Intl_LIBRARIES}
)
target_include_directories(libptouchSwig PUBLIC
	${CMAKE_BINARY_DIR}	# HB9HEI - location of generated version.h
	${CMAKE_SOURCE_DIR}/include
	${GD_INCLUDE_DIR}
	${LIBUSB_INCLUDE_DIRS}
	${Intl_INCLUDE_DIRS}
)
set_target_properties(libptouchSwig
	PROPERTIES
	LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/pyTouch
)

install(TARGETS ${PROJECT_NAME} DESTINATION bin)

install(TARGETS ptouch DESTINATION lib)
install(FILES include/ptouch.h DESTINATION include)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/ptouch-print.1 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)
