from pathlib import Path

p = Path("jacobi.cpp")
src = p.read_text()

# Locate the original final validation block.
begin = "    int result_correct = 1;"
end = "    result_correct = global_result_correct;"

if src.count(begin) != 1 or src.count(end) != 1:
    raise SystemExit(
        "Cannot identify validation block uniquely. "
        "Inspect the source before patching."
    )

i = src.index(begin)
j = src.index(end, i) + len(end)

replacement = r'''    // Strict numerical validation of every owned interior point.
    int result_correct = 1;
    unsigned long long checked = 0;
    unsigned long long nonfinite = 0;
    unsigned long long mismatches = 0;
    double max_abs_error = 0.0;

    // iy_end_global is inclusive.
    for (int iy = iy_start_global; iy <= iy_end_global; ++iy) {
        for (int ix = 1; ix < nx - 1; ++ix) {
            const unsigned long long idx =
                static_cast<unsigned long long>(iy) * nx + ix;

            const real ref = a_ref_h[idx];
            const real got = a_h[idx];

            ++checked;

            const bool finite =
                std::isfinite(ref) && std::isfinite(got);

            if (!finite) {
                ++nonfinite;

                if (result_correct) {
                    fprintf(stderr,
                        "ERROR rank %d: non-finite value "
                        "at (%d,%d): got=%g ref=%g\n",
                        rank, iy, ix,
                        static_cast<double>(got),
                        static_cast<double>(ref));
                }

                result_correct = 0;
                continue;
            }

            const double err = std::fabs(
                static_cast<double>(got) -
                static_cast<double>(ref));

            max_abs_error = std::max(max_abs_error, err);

            if (err > static_cast<double>(tol)) {
                ++mismatches;

                if (result_correct) {
                    fprintf(stderr,
                        "ERROR rank %d: mismatch at (%d,%d): "
                        "got=%.12g ref=%.12g error=%.12g\n",
                        rank, iy, ix,
                        static_cast<double>(got),
                        static_cast<double>(ref), err);
                }

                result_correct = 0;
            }
        }
    }

    unsigned long long local_counts[3] = {
        checked, nonfinite, mismatches
    };

    unsigned long long global_counts[3] = {0, 0, 0};

    MPI_CALL(MPI_Allreduce(
        local_counts, global_counts, 3,
        MPI_UNSIGNED_LONG_LONG, MPI_SUM, MPI_COMM_WORLD));

    double global_max_error = 0.0;

    MPI_CALL(MPI_Allreduce(
        &max_abs_error, &global_max_error, 1,
        MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD));

    const unsigned long long expected =
        static_cast<unsigned long long>(ny - 2) * (nx - 2);

    if (global_counts[0] != expected ||
        global_counts[1] != 0 ||
        global_counts[2] != 0) {
        result_correct = 0;
    }

    int global_result_correct = 1;

    MPI_CALL(MPI_Allreduce(
        &result_correct, &global_result_correct, 1,
        MPI_INT, MPI_MIN, MPI_COMM_WORLD));

    result_correct = global_result_correct;

    if (rank == 0) {
        printf(
            "STRICT_VALIDATION: %s "
            "checked=%llu expected=%llu "
            "nonfinite=%llu mismatches=%llu "
            "max_abs_error=%.12g tol=%.12g\n",
            result_correct ? "PASS" : "FAIL",
            global_counts[0], expected,
            global_counts[1], global_counts[2],
            global_max_error,
            static_cast<double>(tol));
    }
'''

p.write_text(src[:i] + replacement + src[j:])
print("Strict numerical validation installed.")
