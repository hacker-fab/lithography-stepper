#include "config.hpp"
#include "ControlInterface.hpp"
#include <Python.h>

ControlInterface::ControlInterface() {
    // Initialize the Python interpreter
    Py_Initialize();
    // This is important as if you dont import sys and add current path to sys path, C can not locate python module.
    PyRun_SimpleString("import sys");
    //PyRun_SimpleString("print('This is a test to see if python works')");
    // Add current path to sys path. Change path if needed.
    PyRun_SimpleString("sys.path.append('../scripts/')");
    // Import the Python module (dont add .py, just the name of your python module/script)
    PyObject *pName = PyUnicode_DecodeFSDefault("Lithographer");
    PyObject *pModule = PyImport_Import(pName);
    Py_XDECREF(pName);

    // Check if the module was imported successfully
    if (pModule != NULL) {
    	// Pass a pointer to C memory using this object
        /*
        PyObject *mem = PyMemoryView_FromMemory(reinterpret_cast<char *>(&fmt), sizeof(fmt), PyBUF_READ);
        
        // Use this tuple to pass data to the Python module
        PyObject *dataToPass = PyTuple_New(1);
        PyTuple_SET_ITEM(dataToPass, 0, mem);
        
        // Get a reference to the Python function
        PyObject *pFunc = PyObject_GetAttrString(pModule, "hello");

        // Check if the function exists
        if (PyCallable_Check(pFunc)) {
            // Call the Python function
            PyObject_CallObject(pFunc, dataToPass);
        } else {
            PyErr_Print();
        }
        

        // Decrement reference counts and clean up (This will end python kernel, if you wan to invoke python kernel again, 
        // simply repeat previous code)
        Py_XDECREF(pFunc);
        */
        Py_DECREF(pModule);
    } else {
        PyErr_Print();
        DEBUG_OUTPUT("wewewewe");
    }

    // Finalize the Python interpreter
    Py_Finalize();
}

void ControlInterface::updateData() {

}
