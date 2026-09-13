cmake_minimum_required(VERSION 3.15)

project(ptouch-print C)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")

option(BUILD_PYPTOUCH "Build PyPTouch's Swig Interface" OFF)

include(GNUInstallDirs)
# set(CMAKE_INSTALL_PREFIX /usr)
set(CMAKE_C_STANDARD 11)

# Configure required dependencies
find_package(Gettext REQUIRED)
find_package(GD REQUIRED)
find_package(Git REQUIRED)
find_package(PkgConfig REQUIRED)
find_package(Intl REQUIRED)

pkg_check_modules(LIBUSB REQUIRED libusb-1.0)

if(BUILD_PYPTOUCH)
    find_package(SWIG REQUIRED)
	include(UseSWIG)
	find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
endif(BUILD_PYPTOUCH)

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

target_sources(ptouch PRIVATE
	include/ptouch.h
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

target_sources(${PROJECT_NAME} PRIVATE
	include/ptouch.h
	src/ptouch-print.c
)

add_dependencies(${PROJECT_NAME}
	git-version
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
)

# HB9HEI - custom target that produces version.h	(req. cmake 3.0)
add_custom_target(git-version ALL
	${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/gitversion.cmake
)

if(BUILD_PYPTOUCH)
	if(NOT DEFINED PYTOUCH_OUTPUT_DIR)
		set(PYTOUCH_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/pyPTouch")
	endif()

    SWIG_ADD_LIBRARY(libptouchSwig
		TYPE MODULE
		LANGUAGE python
		OUTFILE_DIR ${CMAKE_CURRENT_BINARY_DIR}
		OUTPUT_DIR ${PYTOUCH_OUTPUT_DIR}
		SOURCES
	        pyPTouch/libptouch.i
    	    include/ptouch.h
        	src/libptouch.c
    )
    target_link_libraries(libptouchSwig PUBLIC
		Python3::Module
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
endif(BUILD_PYPTOUCH)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/gettext.cmake)

install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_BINDIR})

install(TARGETS ptouch DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES include/ptouch.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/ptouch-print.1 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

if(EXISTS /etc/udev/rules.d)
	install(FILES udev/20-usb-ptouch-permissions.rules DESTINATION /etc/udev/rules.d)
	install(CODE "execute_process(COMMAND udevadm control --reload-rules)")
endif()
