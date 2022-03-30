import numpy as np
import pytest
import pyccl as ccl
from pyccl.pyutils import assert_warns


COSMO = ccl.Cosmology(
    Omega_c=0.27, Omega_b=0.045, h=0.67, sigma8=0.8, n_s=0.96,
    transfer_function='bbks', matter_power_spectrum='linear')
M200 = ccl.halos.MassDef200m()
HMF = ccl.halos.MassFuncTinker10(COSMO, mass_def=M200)
HBF = ccl.halos.HaloBiasTinker10(COSMO, mass_def=M200)
P1 = ccl.halos.HaloProfileNFW(ccl.halos.ConcentrationDuffy08(M200),
                              fourier_analytic=True)
P2 = ccl.halos.HaloProfileHOD(ccl.halos.ConcentrationDuffy08(M200))
P3 = ccl.halos.HaloProfilePressureGNFW()
P4 = P1
Pneg = ccl.halos.HaloProfilePressureGNFW(P0=-1)
PKC = ccl.halos.Profile2pt()
PKCH = ccl.halos.Profile2ptHOD()
KK = np.geomspace(1E-3, 10, 32)
MM = np.geomspace(1E11, 1E15, 16)
AA = 1.0
PSP = ccl.Pk2D.pk_from_model(COSMO, 'bbks')


def smoke_assert_tkk2h_real(func):
    sizes = [(0, 0),
             (2, 0),
             (0, 2),
             (2, 3),
             (1, 3),
             (3, 1)]
    shapes = [(),
              (2,),
              (2, 2,),
              (2, 3, 3),
              (1, 3, 3),
              (3, 1, 1)]
    for (sa, sk), sh in zip(sizes, shapes):
        if sk == 0:
            k = 0.1
        else:
            k = np.logspace(-2., 0., sk)
        if sa == 0:
            a = 1.
        else:
            a = np.linspace(0.5, 1., sa)
        p = func(k, a)
        assert np.shape(p) == sh
        assert np.all(np.isfinite(p))


@pytest.mark.parametrize('pars',
                         [{'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'norm': False, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': P4,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': None, 'cv14': None, 'cv24': PKCH, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': None, 'cv24': PKCH, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': None, 'cv24': PKC, 'cv32':
                           None, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': PKC, 'cv24': PKC, 'cv32':
                           PKCH, 'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': PKC, 'cv24': PKC, 'cv32':
                           PKCH, 'norm': True, 'p_of_k_a': 'linear'},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': PKC, 'cv24': PKC, 'cv32':
                           PKCH, 'norm': True, 'p_of_k_a': 'nonlinear'},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv13': PKC, 'cv14': PKC, 'cv24': PKC, 'cv32': PKCH,
                           'norm': True, 'p_of_k_a': PSP},
                          ])
def test_tkk2h_22_smoke(pars):
    hmc = ccl.halos.HMCalculator(COSMO, HMF, HBF, mass_def=M200,
                                 nlog10M=2)

    def f(k, a):
        return ccl.halos.halomod_trispectrum_2h_22(COSMO, hmc, k, a,
                                                   prof1=pars['p1'],
                                                   prof2=pars['p2'],
                                                   prof3=pars['p3'],
                                                   prof4=pars['p4'],
                                                   prof13_2pt=pars['cv13'],
                                                   prof14_2pt=pars['cv14'],
                                                   prof24_2pt=pars['cv24'],
                                                   prof32_2pt=pars['cv32'],
                                                   normprof1=pars['norm'],
                                                   normprof2=pars['norm'],
                                                   normprof3=pars['norm'],
                                                   normprof4=pars['norm'],
                                                   p_of_k_a=pars['p_of_k_a'])
    smoke_assert_tkk2h_real(f)


@pytest.mark.parametrize('pars',
                         [{'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv12': None, 'cv34': None,
                           'norm': False, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': None, 'p4': None,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': P4,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': None, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': None, 'cv34': None,
                           'cv124': None, 'cv123': None, 'norm': True,
                           'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': PKC, 'cv34': None,
                           'norm': True, 'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': None, 'cv34': PKC, 'norm': True,
                           'p_of_k_a': None},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': PKC, 'cv34': PKC,
                           'norm': True, 'p_of_k_a': 'linear'},
                          {'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': PKC, 'cv34': PKC, 'norm': True,
                           'p_of_k_a': 'nonlinear'},
                          # Test HOD: p1 and p2 must be HOD profiles
                          {'p1': P2, 'p2': P2, 'p3': P3, 'p4': P4,
                           'cv12': PKCH, 'cv34': PKC, 'norm': True,
                           'p_of_k_a': PSP},
                          ])
def test_tkk2h_13_smoke(pars):
    hmc = ccl.halos.HMCalculator(COSMO, HMF, HBF, mass_def=M200,
                                 nlog10M=2)

    def f(k, a):
        return ccl.halos.halomod_trispectrum_2h_13(COSMO, hmc, k, a,
                                                   prof1=pars['p1'],
                                                   prof2=pars['p2'],
                                                   prof3=pars['p3'],
                                                   prof4=pars['p4'],
                                                   prof12_2pt=pars['cv12'],
                                                   prof34_2pt=pars['cv34'],
                                                   normprof1=pars['norm'],
                                                   normprof2=pars['norm'],
                                                   normprof3=pars['norm'],
                                                   normprof4=pars['norm'],
                                                   p_of_k_a=pars['p_of_k_a'])
    smoke_assert_tkk2h_real(f)


def test_Tk3D_2h():
    hmc = ccl.halos.HMCalculator(COSMO, HMF, HBF, mass_def=M200)
    k_arr = KK
    a_arr = np.array([0.1, 0.4, 0.7, 1.0])
    tkk_arr = ccl.halos.halomod_trispectrum_2h_22(COSMO, hmc, k_arr, a_arr,
                                                  P1, prof2=P2,
                                                  prof3=P3, prof4=P4,
                                                  prof13_2pt=PKC,
                                                  prof14_2pt=PKC,
                                                  prof24_2pt=PKC,
                                                  prof32_2pt=PKC,
                                                  normprof1=True,
                                                  normprof2=True,
                                                  normprof3=True,
                                                  normprof4=True,
                                                  p_of_k_a=None)

    tkk_arr += ccl.halos.halomod_trispectrum_2h_13(COSMO, hmc, k_arr, a_arr,
                                                   prof1=P1, prof2=P2,
                                                   prof3=P3, prof4=P4,
                                                   prof12_2pt=None,
                                                   prof34_2pt=None,
                                                   normprof1=True,
                                                   normprof2=True,
                                                   normprof3=True,
                                                   normprof4=True,
                                                   p_of_k_a=None)

    # Input sampling
    tk3d = ccl.halos.halomod_Tk3D_2h(COSMO, hmc,
                                     P1, prof2=P2,
                                     prof3=P3, prof4=P4,
                                     prof13_2pt=PKC,
                                     prof14_2pt=PKC,
                                     prof24_2pt=PKC,
                                     prof32_2pt=PKC,
                                     prof12_2pt=PKC,
                                     prof34_2pt=PKC,
                                     normprof1=True,
                                     normprof2=True,
                                     normprof3=True,
                                     normprof4=True,
                                     p_of_k_a=None,
                                     lk_arr=np.log(k_arr),
                                     a_arr=a_arr,
                                     use_log=True)
    tkk_arr_2 = np.array([tk3d.eval(k_arr, a) for a in a_arr])
    assert np.all(np.fabs((tkk_arr / tkk_arr_2 - 1)).flatten()
                  < 1E-4)

    # Standard sampling
    tk3d = ccl.halos.halomod_Tk3D_2h(COSMO, hmc,
                                     P1, prof2=P2,
                                     prof3=P3, prof4=P4,
                                     prof13_2pt=PKC,
                                     prof14_2pt=PKC,
                                     prof24_2pt=PKC,
                                     prof12_2pt=PKC,
                                     prof34_2pt=PKC,
                                     normprof1=True,
                                     normprof2=True,
                                     normprof3=True,
                                     normprof4=True,
                                     p_of_k_a=None,
                                     lk_arr=np.log(k_arr),
                                     use_log=True)
    tkk_arr_2 = np.array([tk3d.eval(k_arr, a) for a in a_arr])
    assert np.all(np.fabs((tkk_arr / tkk_arr_2 - 1)).flatten()
                  < 1E-4)

    # Negative profile in logspace
    assert_warns(ccl.CCLWarning, ccl.halos.halomod_Tk3D_2h,
                 COSMO, hmc, P3, prof2=Pneg,
                 lk_arr=np.log(k_arr), a_arr=a_arr,
                 use_log=True)


@pytest.mark.parametrize('pars',
                         # Wrong first profile
                         [{'p1': None, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          # Wrong other profiles
                          {'p1': P1, 'p2': PKC, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': PKC, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': PKC,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': P2, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          # Wrong 2pts
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': P2, 'cv14': P2, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': P2, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': P2, 'cv32':
                           None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           P2, 'p_of_k_a': None},
                          # Wrong p_of_k_a
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv13': None, 'cv14': None, 'cv24': None, 'cv32':
                           None, 'p_of_k_a': P2},
                          ])
def test_tkk2h_22_errors(pars):

    hmc = ccl.halos.HMCalculator(COSMO, HMF, HBF, mass_def=M200)
    k_arr = KK
    a_arr = np.array([0.1, 0.4, 0.7, 1.0])

    with pytest.raises(TypeError):
        ccl.halos.halomod_trispectrum_2h_22(COSMO, hmc, k_arr, a_arr,
                                            prof1=pars['p1'], prof2=pars['p2'],
                                            prof3=pars['p3'], prof4=pars['p4'],
                                            prof13_2pt=pars['cv13'],
                                            prof14_2pt=pars['cv14'],
                                            prof24_2pt=pars['cv24'],
                                            prof32_2pt=pars['cv32'],
                                            p_of_k_a=pars['p_of_k_a'])


@pytest.mark.parametrize('pars',
                         # Wrong first profile
                         [{'p1': None, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          # Wrong other profiles
                          {'p1': P1, 'p2': PKC, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': PKC, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': PKC,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          # Wrong 2pts
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': P2, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': P2, 'cv124': None,
                           'cv123': None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': P2,
                           'cv123': None, 'p_of_k_a': None},
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': P2, 'p_of_k_a': None},
                          # Wrong p_of_k_a
                          {'p1': P1, 'p2': None, 'p3': None, 'p4': None,
                           'cv234': None, 'cv134': None, 'cv124': None,
                           'cv123': None, 'p_of_k_a': P2},
                          ])
def test_tkk2h_13_errors(pars):

    hmc = ccl.halos.HMCalculator(COSMO, HMF, HBF, mass_def=M200)
    k_arr = KK
    a_arr = np.array([0.1, 0.4, 0.7, 1.0])

    with pytest.raises(TypeError):
        ccl.halos.halomod_trispectrum_2h_13(COSMO, hmc, k_arr, a_arr,
                                            prof1=pars['p1'],
                                            prof2=pars['p2'],
                                            prof3=pars['p3'],
                                            prof4=pars['p4'],
                                            prof234_3pt=pars['cv234'],
                                            prof134_3pt=pars['cv134'],
                                            prof124_3pt=pars['cv124'],
                                            prof123_3pt=pars['cv123'],
                                            p_of_k_a=pars['p_of_k_a'])
