using Pkg
ENV["PYTHON"] = abspath("venv/bin/python")
Pkg.build("PyCall")
using PackageCompiler
PackageCompiler.create_sysimage(; sysimage_path="JuliaSysimage.so",
                                     precompile_execution_file="stage_simulate.jl")