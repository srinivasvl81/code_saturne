!-------------------------------------------------------------------------------

! This file is part of Code_Saturne, a general-purpose CFD tool.
!
! Copyright (C) 1998-2013 EDF S.A.
!
! This program is free software; you can redistribute it and/or modify it under
! the terms of the GNU General Public License as published by the Free Software
! Foundation; either version 2 of the License, or (at your option) any later
! version.
!
! This program is distributed in the hope that it will be useful, but WITHOUT
! ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
! FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
! details.
!
! You should have received a copy of the GNU General Public License along with
! this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
! Street, Fifth Floor, Boston, MA 02110-1301, USA.

!-------------------------------------------------------------------------------

subroutine divmas &
!================

 ( ncelet , ncel   , nfac   , nfabor ,                            &
   init   , nfecra ,                                              &
   ifacel , ifabor ,                                              &
   flumas , flumab ,                                              &
   diverg )

!===============================================================================
! FONCTION :
! ----------

! INTEGRATION DU FLUX DE MASSE SUR LES CELLULES

!  .    .       --  .
!  m =  m     + \   m
!   i    i      /__  ij
!                  j

!-------------------------------------------------------------------------------
! Arguments
!__________________.____._____.________________________________________________.
! name             !type!mode ! role                                           !
!__________________!____!_____!________________________________________________!
! ncelet           ! i  ! <-- ! number of extended (real + ghost) cells        !
! ncel             ! i  ! <-- ! number of cells                                !
! nfac             ! i  ! <-- ! number of interior faces                       !
! nfabor           ! i  ! <-- ! number of boundary faces                       !
! init             ! e  ! <-- ! indicateur > 0 remise a 0 de diverg            !
! ifacel(2,nfac    ! te ! <-- ! no des elts voisins d'une face intern          !
! ifabor(nfabor    ! te ! <-- ! no de l'elt voisin d'une face de bord          !
! flumas(nfac)     ! tr ! <-- ! flux de masse aux faces internes               !
! flumab(nfabor    ! tr ! <-- ! flux de masse aux faces de bord                !
! diverg(ncelet    ! tr ! <-- ! divergence de flumas flumab                    !
!__________________!____!_____!________________________________________________!

!     TYPE : E (ENTIER), R (REEL), A (ALPHANUMERIQUE), T (TABLEAU)
!            L (LOGIQUE)   .. ET TYPES COMPOSES (EX : TR TABLEAU REEL)
!     MODE : <-- donnee, --> resultat, <-> Donnee modifiee
!            --- tableau de travail
!===============================================================================

!===============================================================================
! Module files
!===============================================================================

use parall

!===============================================================================

implicit none

integer          ncelet , ncel   , nfac   , nfabor
integer          init   , nfecra

integer          ifacel(2,nfac), ifabor(nfabor)
double precision flumas(nfac), flumab(nfabor)
double precision diverg(ncelet)

! Local variables

integer          iel, ifac, ii, jj, ig, it

!===============================================================================

!===============================================================================
! 1.  INITIALISATION
!===============================================================================

if (init.ge.1) then
  !$omp parallel do
  do iel = 1, ncelet
    diverg(iel) = 0.d0
  enddo
elseif (init.eq.0.and.ncelet.gt.ncel) then
  !$omp parallel do if(ncelet - ncel > thr_n_min)
  do iel = ncel+1, ncelet
    diverg(iel) = 0.d0
  enddo
elseif (init.ne.0) then
  write(nfecra,1000) init
  call csexit (1)
endif


!===============================================================================
! 2.  INTEGRATION SUR LES FACETTES INTERNES
!===============================================================================

do ig = 1, ngrpi
  !$omp parallel do private(ifac, ii, jj)
  do it = 1, nthrdi
    do ifac = iompli(1,ig,it), iompli(2,ig,it)

      ii = ifacel(1,ifac)
      jj = ifacel(2,ifac)
      diverg(ii) = diverg(ii) + flumas(ifac)
      diverg(jj) = diverg(jj) - flumas(ifac)

    enddo
  enddo
enddo


!===============================================================================
! 3.  INTEGRATION SUR LES FACETTES DE BORD
!===============================================================================

do ig = 1, ngrpb
  !$omp parallel do private(ifac, ii) if(nfabor > thr_n_min)
  do it = 1, nthrdb
    do ifac = iomplb(1,ig,it), iomplb(2,ig,it)

      ii = ifabor(ifac)
      diverg(ii) = diverg(ii) + flumab(ifac)

    enddo
  enddo
enddo

#if defined(_CS_LANG_FR)

 1000 format('DIVMAS APPELE AVEC INIT = ',I10)

#else

 1000 format('DIVMAS CALLED WITH INIT = ',I10)

#endif

!----
! End
!----

return

end subroutine