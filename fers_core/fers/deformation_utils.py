import numpy as np


# Helper: Build rotation matrix from local axes
def get_rotation_matrix(local_x, local_y, local_z):
    # Each is shape (3,). We'll stack them as columns
    R = np.column_stack([local_x, local_y, local_z])  # shape (3,3)
    return R


# Helper: Transform global DOFs to local
def transform_dofs_global_to_local(d_global, r_global, R):
    # local_disp = R^T * global_disp
    d_local = R.T @ d_global
    r_local = R.T @ r_global
    return d_local, r_local


# Helper: Interpolate in local coords. You can do something more sophisticated
# with shape functions, but here's a simple approach to show the concept.
def interpolate_beam_local(
    xstart, xend, local_disp_start, local_disp_end, local_rot_start, local_rot_end, n_points
):
    """
    xstart, xend = scalar or local length in the local x-axis
    local_disp_start, local_disp_end = (u_x, u_y, u_z) at ends
    local_rot_start, local_rot_end   = (phi_x, phi_y, phi_z) at ends
    n_points = how many interpolation points.

    Returns: an array shape (n_points, 3) of deflections in local coordinates,
            for x from 0..(xend-xstart).
    """
    # For demonstration, let's do a simple "cubic" in local y and z for bending,
    # plus linear in x and maybe a twist for phi_x. This is not a full 3D shape function,
    # but gives an idea.

    # We'll param = t in [0..1], length L = (xend - xstart)
    # local_y(t) and local_z(t) as cubic polynomials matching end deflections and slopes
    import numpy as np

    L = xend - xstart
    t = np.linspace(0, 1, n_points)

    # local_disp_start = [uxs, uys, uzs]
    # local_disp_end   = [uxe, uye, uze]
    uxs, uys, uzs = local_disp_start
    uxe, uye, uze = local_disp_end

    # local_rot_start = [rxs, rys, rzs]  (these are small-angle rotations about local x,y,z)
    # Typically, for Euler-Bernoulli beam bending about y or z, we'd use phi_z or phi_y as slope.
    # We'll do something simple: the slope in yz-plane depends on phi_z or phi_y.

    # For "bending in y", slope ~ phi_z (rotation about local z).
    # For "bending in z", slope ~ -phi_y (rotation about local y).
    # This is a big simplification!

    rxs, rys, rzs = local_rot_start
    rxe, rye, rze = local_rot_end

    # 1) Interpolate in local x as linear
    ux_vals = uxs + (uxe - uxs) * t

    # 2) Interpolate local y with a "cubic Hermite" style
    #    y(0)=uys, y(L)=uye, y'(0)=slope0, y'(L)=slope1
    #    slope0 ~ L * ( rotation about z at start )
    slope_y0 = L * rzs  # approximate slope from rotation about z
    slope_y1 = L * rze  # at end

    # Hermite basis for t in [0..1]
    # h1 = 2t^3 - 3t^2 + 1
    # h2 = -2t^3 + 3t^2
    # h3 = t^3 - 2t^2 + t
    # h4 = t^3 - t^2
    # y(t) = uys*h1 + uye*h2 + slope_y0*h3 + slope_y1*h4
    h1 = 2 * t**3 - 3 * t**2 + 1
    h2 = -2 * t**3 + 3 * t**2
    h3 = t**3 - 2 * t**2 + t
    h4 = t**3 - t**2

    y_vals = uys * h1 + uye * h2 + slope_y0 * h3 + slope_y1 * h4

    # 3) Interpolate local z similarly, slope from rotation about y
    slope_z0 = -L * rys
    slope_z1 = -L * rye
    z_vals = uzs * h1 + uze * h2 + slope_z0 * h3 + slope_z1 * h4

    # Combine
    deflections_local = np.vstack([ux_vals, y_vals, z_vals]).T  # shape (n_points, 3)
    return deflections_local
