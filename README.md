You can install multiple versions and compiler variants of openmpi in parallel
with:

    yum install openmpi%version%-%variant%

This will install an environment module of the name:

    mpi/openmpi-%variant%/%version%-%arch%

To use you can use either of:

    module load mpi
    module load mpi/openmpi-%variant%
    module load mpi/openmpi-%variant%/%version%-%arch%

with increasing order of specificity of mpi type/variant and version.
