#include <Python.h>
#include <fribidi/fribidi.h>

#if PY_MAJOR_VERSION >= 3
#define PyString_AsString PyUnicode_AsUTF8
#define PYSTRING_Length PyUnicode_GetLength
#define PYSTRING_FromString PyUnicode_FromString
#else
#define PYSTRING_AsString PyString_AsString
#define PYSTRING_Length PyString_Size
#define PYSTRING_FromString PyUnicode_FromString
#endif

/* This is easier than trying to figure out the header that alloca is */
/* defined in. */
void *alloca(size_t size);

PyObject *renpybidi_log2vis(PyObject *s, int *direction) {
    char *src;
    Py_ssize_t size;
    FriBidiChar *srcuni;
    int unisize;
    FriBidiChar *dstuni;
    char *dst;
    
    src = PYSTRING_AsString(s);

    if (src == NULL) {
        return NULL;
    }

    size = PYSTRING_Length(s);

    srcuni = (FriBidiChar *) alloca(size * 4);
    dstuni = (FriBidiChar *) alloca(size * 4);
    dst = (char *) alloca(size * 4);
    
    unisize = fribidi_charset_to_unicode(FRIBIDI_CHAR_SET_UTF8, src, size, srcuni);

    fribidi_log2vis(
        srcuni,
        unisize,
        direction,
        dstuni,
        NULL,
        NULL,
        NULL);

    fribidi_unicode_to_charset(FRIBIDI_CHAR_SET_UTF8, dstuni, unisize, dst);

    return PYSTRING_FromString(dst);
}
