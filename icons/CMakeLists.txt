# Generate a compiled resource file for any icons we are using and install it into the appropriate
# location.

# Convert our icons resource file into a Python file via the available PySide
# resource compiler. Houdini 21 uses Qt6/PySide6 by default, while older
# supported Houdini builds may still use Qt5/PySide2.
if("$ENV{HOUDINI_TOOLBOX_QT_BINDING}" STREQUAL "PySide2")
    find_program(QT_RCC NAMES pyside2-rcc REQUIRED)
elseif("$ENV{HOUDINI_TOOLBOX_QT_BINDING}" STREQUAL "PySide6")
    find_program(QT_RCC NAMES pyside6-rcc REQUIRED)
elseif("$ENV{HOUDINI_TOOLBOX_QT_BINDING}" STREQUAL "PyQt5")
    find_program(QT_RCC NAMES pyrcc5 REQUIRED)
elseif("$ENV{HOUDINI_TOOLBOX_QT_BINDING}" STREQUAL "PyQt6")
    find_program(QT_RCC NAMES pyrcc6 pyqt6-rcc REQUIRED)
else()
    find_program(QT_RCC NAMES pyside6-rcc pyside2-rcc pyrcc6 pyqt6-rcc pyrcc5 REQUIRED)
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
