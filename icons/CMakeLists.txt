# Generate a compiled resource file for any icons we are using and install it into the appropriate
# location.

# Convert our icons resource file into a Python file via the resource compiler
# matching the targeted Houdini Qt binding. Houdini 21 uses Qt6/PySide6 by
# default, while older supported Houdini builds use Qt5/PySide2.
set(HT_QT_BINDING "$ENV{HOUDINI_TOOLBOX_QT_BINDING}")

if(NOT HT_QT_BINDING)
    if("$ENV{REZ_HOUDINI_VERSION}" MATCHES "^21\\.")
        set(HT_QT_BINDING "PySide6")
    elseif("$ENV{REZ_HOUDINI_VERSION}" MATCHES "^(19|20)\\.")
        set(HT_QT_BINDING "PySide2")
    elseif("$ENV{HFS}" MATCHES "(^|[^0-9])21[._]")
        set(HT_QT_BINDING "PySide6")
    elseif("$ENV{HFS}" MATCHES "(^|[^0-9])(19|20)[._]")
        set(HT_QT_BINDING "PySide2")
    else()
        set(HT_QT_BINDING "PySide2")
    endif()
endif()

if(HT_QT_BINDING STREQUAL "PySide2")
    find_program(QT_RCC NAMES pyside2-rcc REQUIRED)
elseif(HT_QT_BINDING STREQUAL "PySide6")
    find_program(QT_RCC NAMES pyside6-rcc REQUIRED)
elseif(HT_QT_BINDING STREQUAL "PyQt5")
    find_program(QT_RCC NAMES pyrcc5 REQUIRED)
elseif(HT_QT_BINDING STREQUAL "PyQt6")
    find_program(QT_RCC NAMES pyrcc6 pyqt6-rcc REQUIRED)
else()
    message(FATAL_ERROR "Unsupported Qt binding: ${HT_QT_BINDING}")
endif()

execute_process(
    COMMAND ${QT_RCC} -o $ENV{REZ_BUILD_PATH}/icons/icons.py ${CMAKE_CURRENT_SOURCE_DIR}/icons.qrc
    COMMAND_ECHO STDOUT
)

# Install the icons.py file into the main Python area.
install(
    FILES
    "$ENV{REZ_BUILD_PATH}/icons/icons.py"
    DESTINATION
    "$ENV{REZ_BUILD_INSTALL_PATH}/python/houdini_toolbox/ui"
)
