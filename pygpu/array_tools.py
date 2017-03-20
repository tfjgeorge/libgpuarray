from string import Template
from .gpuarray import GpuArray, GpuKernel


def _generate_kernel(ctx, cols, upper=True):
    tmpl = Template("""
    KERNEL void extract_tri(ga_float *a, ga_uint N) {
        unsigned int idx = blockIdx.y*blockDim.x*gridDim.x+
                           blockIdx.x*blockDim.x+threadIdx.x;
        unsigned int ix = idx/${cols};
        unsigned int iy = idx%${cols};
        if (idx < N) {
            if (ix ${le} iy)
                a[idx] = 0.0;
        }
    }
    """)
    if upper:
        le = '>'
    else:
        le = '<'
    src = tmpl.substitute(cols=cols, le=le)
    spec = [GpuArray, 'uint32']
    k = GpuKernel(src, "extract_tri", spec, context=ctx)
    return k


def triu(A, ctx, inplace=True):
    if not inplace:
        A = A.copy()
    upper = True
    if A.flags['F_CONTIGUOUS']:
        upper = False
    k = _generate_kernel(ctx, A.shape[0], upper)
    k(A, A.shape[0] * A.shape[1], n=A.shape[0] * A.shape[1])
    return A


def tril(A, ctx, inplace=True):
    if not inplace:
        A = A.copy()
    upper = False
    if A.flags['F_CONTIGUOUS']:
        upper = True
    k = _generate_kernel(ctx, A.shape[0], upper)
    k(A, A.shape[0] * A.shape[1], n=A.shape[0] * A.shape[1])
    return A