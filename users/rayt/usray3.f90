!-------------------------------------------------------------------------------

!VERS


!     This file is part of the Code_Saturne Kernel, element of the
!     Code_Saturne CFD tool.

!     Copyright (C) 1998-2009 EDF S.A., France

!     contact: saturne-support@edf.fr

!     The Code_Saturne Kernel is free software; you can redistribute it
!     and/or modify it under the terms of the GNU General Public License
!     as published by the Free Software Foundation; either version 2 of
!     the License, or (at your option) any later version.

!     The Code_Saturne Kernel is distributed in the hope that it will be
!     useful, but WITHOUT ANY WARRANTY; without even the implied warranty
!     of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!     GNU General Public License for more details.

!     You should have received a copy of the GNU General Public License
!     along with the Code_Saturne Kernel; if not, write to the
!     Free Software Foundation, Inc.,
!     51 Franklin St, Fifth Floor,
!     Boston, MA  02110-1301  USA

!-------------------------------------------------------------------------------

subroutine usray3 &
!================

 ( idbia0 , idbra0 ,                                              &
   ndim   , ncelet , ncel   , nfac   , nfabor , nfml   , nprfml , &
   nnod   , lndfac , lndfbr , ncelbr ,                            &
   nvar   , nscal  , iphas  , iappel ,                            &
   nideve , nrdeve , nituse , nrtuse ,                            &
   ifacel , ifabor , ifmfbr , ifmcel , iprfml , itypfb ,          &
   ipnfac , nodfac , ipnfbr , nodfbr , izfrdp ,                   &
   idevel , ituser , ia     ,                                     &
   xyzcen , surfac , surfbo , cdgfac , cdgfbo , xyznod , volume , &
   dt     , rtp    , rtpa   , propce , propfa , propfb ,          &
   ck     , w1     , w2     , w3     , w4     , w5     ,  w6    , &
   rdevel , rtuser ,                                              &
   ra     )

!===============================================================================
! FONCTION :
! ----------

!   SOUS-PROGRAMME DU MODULE DE RAYONNEMENT :
!   -----------------------------------------


!     Coefficient d'absorption
!    -------------------------

!      Il est indispensable de renseigner la valeur du coefficient
!        d'absorption du fluide CK.

!      Pour un milieu transparent, le coefficient doit etre
!        fixe a 0.D0.

!  DANS LE CAS DU MODELE P-1 ON VERIFIE QUE LA LONGUEUR OPTIQUE
!    DU MILIEU EST AU MINIMUM DE L'ORDRE DE L'UNITE

!      ATTENTION :
!      =========
!        Pour les physiques particulieres (Combustion, charbon...)

!        il est INTERDIT de fournir le COEFFICIENT D'ABSORPTION ici.
!               ========

!        Voir le sous-programme PPCABS


!-------------------------------------------------------------------------------
!ARGU                             ARGUMENTS
!__________________.____._____.________________________________________________.
! name             !type!mode ! role                                           !
!__________________!____!_____!________________________________________________!
! idbia0           ! i  ! <-- ! number of first free position in ia            !
! idbra0           ! i  ! <-- ! number of first free position in ra            !
! ndim             ! i  ! <-- ! spatial dimension                              !
! ncelet           ! i  ! <-- ! number of extended (real + ghost) cells        !
! ncel             ! i  ! <-- ! number of cells                                !
! nfac             ! i  ! <-- ! number of interior faces                       !
! nfabor           ! i  ! <-- ! number of boundary faces                       !
! nfml             ! i  ! <-- ! number of families (group classes)             !
! nprfml           ! i  ! <-- ! number of properties per family (group class)  !
! nnod             ! i  ! <-- ! number of vertices                             !
! lndfac           ! i  ! <-- ! size of nodfac indexed array                   !
! lndfbr           ! i  ! <-- ! size of nodfbr indexed array                   !
! ncelbr           ! i  ! <-- ! number of cells with faces on boundary         !
! nvar             ! i  ! <-- ! total number of variables                      !
! nscal            ! i  ! <-- ! total number of scalars                        !
! iphas            ! e  ! <-- ! numero de la phase courante                    !
! nideve, nrdeve   ! i  ! <-- ! sizes of idevel and rdevel arrays              !
! nituse, nrtuse   ! i  ! <-- ! sizes of ituser and rtuser arrays              !
! ifacel(2, nfac)  ! ia ! <-- ! interior faces -> cells connectivity           !
! ifabor(nfabor)   ! ia ! <-- ! boundary faces -> cells connectivity           !
! ifmfbr(nfabor)   ! ia ! <-- ! boundary face family numbers                   !
! ifmcel(ncelet)   ! ia ! <-- ! cell family numbers                            !
! iprfml           ! ia ! <-- ! property numbers per family                    !
!  (nfml, nprfml)  !    !     !                                                !
! itypfb(nfabor    ! te ! <-- ! type des faces de bord                         !
!  nphas      )    !    !     !                                                !
! ipnfac(nfac+1)   ! ia ! <-- ! interior faces -> vertices index (optional)    !
! nodfac(lndfac)   ! ia ! <-- ! interior faces -> vertices list (optional)     !
! ipnfbr(nfabor+1) ! ia ! <-- ! boundary faces -> vertices index (optional)    !
! nodfbr(lndfbr)   ! ia ! <-- ! boundary faces -> vertices list (optional)     !
! izfrdp(nfabor    ! te ! <-- ! numero de zone pour les faces de bord          !
! idevel(nideve)   ! ia ! <-> ! integer work array for temporary development   !
! ituser(nituse)   ! ia ! <-> ! user-reserved integer work array               !
! ia(*)            ! ia ! --- ! main integer work array                        !
! xyzcen           ! ra ! <-- ! cell centers                                   !
!  (ndim, ncelet)  !    !     !                                                !
! surfac           ! ra ! <-- ! interior faces surface vectors                 !
!  (ndim, nfac)    !    !     !                                                !
! surfbo           ! ra ! <-- ! boundary faces surface vectors                 !
!  (ndim, nfabor)  !    !     !                                                !
! cdgfac           ! ra ! <-- ! interior faces centers of gravity              !
!  (ndim, nfac)    !    !     !                                                !
! cdgfbo           ! ra ! <-- ! boundary faces centers of gravity              !
!  (ndim, nfabor)  !    !     !                                                !
! xyznod           ! ra ! <-- ! vertex coordinates (optional)                  !
!  (ndim, nnod)    !    !     !                                                !
! volume(ncelet)   ! ra ! <-- ! cell volumes                                   !
! dt(ncelet)       ! ra ! <-- ! time step (per cell)                           !
! rtp, rtpa        ! ra ! <-- ! calculated variables at cell centers           !
!  (ncelet, *)     !    !     !  (at current and previous time steps)          !
! propce(ncelet, *)! ra ! <-- ! physical properties at cell centers            !
! propfa(nfac, *)  ! ra ! <-- ! physical properties at interior face centers   !
! propfb(nfabor, *)! ra ! <-- ! physical properties at boundary face centers   !
! ck (ncelet)      ! tr ! --> ! coefficient d'absorption du milieu             !
!                  !    !     ! (nul si transparent)                           !
! rdevel(nrdeve)   ! ra ! <-> ! real work array for temporary development      !
! w1...6(ncelet    ! tr ! --- ! tableau de travail                             !
! rtuser(nrtuse)   ! ra ! <-> ! user-reserved real work array                  !
! ra(*)            ! ra ! --- ! main real work array                           !
!__________________!____!_____!________________________________________________!

!     Type: i (integer), r (real), s (string), a (array), l (logical),
!           and composite types (ex: ra real array)
!     mode: <-- input, --> output, <-> modifies data, --- work array
!===============================================================================

implicit none

!===============================================================================
! Common blocks
!===============================================================================

include "paramx.h"
include "numvar.h"
include "entsor.h"
include "optcal.h"
include "cstphy.h"
include "cstnum.h"
include "pointe.h"
include "parall.h"
include "period.h"
include "ppppar.h"
include "ppthch.h"
include "cpincl.h"
include "ppincl.h"
include "radiat.h"
include "ihmpre.h"

!===============================================================================

! Arguments

integer          idbia0 , idbra0
integer          ndim   , ncelet , ncel   , nfac   , nfabor
integer          nfml   , nprfml
integer          nnod   , lndfac , lndfbr , ncelbr
integer          nvar   , nscal  , iphas  , iappel
integer          nideve , nrdeve , nituse , nrtuse

integer          ifacel(2,nfac) , ifabor(nfabor)
integer          ifmfbr(nfabor) , ifmcel(ncelet)
integer          iprfml(nfml,nprfml) , itypfb(nfabor)
integer          ipnfac(nfac+1), nodfac(lndfac)
integer          ipnfbr(nfabor+1), nodfbr(lndfbr),izfrdp(nfabor)
integer          idevel(nideve), ituser(nituse), ia(*)

double precision xyzcen(ndim,ncelet)
double precision surfac(ndim,nfac), surfbo(ndim,nfabor)
double precision cdgfac(ndim,nfac), cdgfbo(ndim,nfabor)
double precision xyznod(ndim,nnod), volume(ncelet)
double precision dt(ncelet), rtp(ncelet,*), rtpa(ncelet,*)
double precision propce(ncelet,*)
double precision propfa(nfac,*), propfb(nfabor,*)

double precision w1(ncelet), w2(ncelet), w3(ncelet)
double precision w4(ncelet), w5(ncelet), w6(ncelet)

double precision ck(ncelet)

double precision rdevel(nrdeve), rtuser(nrtuse), ra(*)


! Local variables

integer          idebia , idebra , iel, ifac, iok
double precision vv, sf, xlc, xkmin, pp

!===============================================================================

! TEST_TO_REMOVE_FOR_USE_OF_SUBROUTINE_START
!===============================================================================

!===============================================================================
! 0.  CE TEST PERMET A L'UTILISATEUR D'ETRE CERTAIN QUE C'EST
!       SA VERSION DU SOUS PROGRAMME QUI EST UTILISEE
!       ET NON CELLE DE LA BIBLIOTHEQUE
!===============================================================================

if (iihmpr.eq.1) then
   return
else
  write(nfecra,9000)
  call csexit (1)
endif

 9000 format(                                                           &
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/,&
'@ @@ ATTENTION : ARRET RAYONNEMENT                           ',/,&
'@    =========                                               ',/,&
'@     LE SOUS-PROGRAMME UTILISATEUR usray3 DOIT ETRE COMPLETE',/,&
'@                                                            ',/,&
'@  Le calcul ne sera pas execute.                            ',/,&
'@                                                            ',/,&
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/)

!===============================================================================
! TEST_TO_REMOVE_FOR_USE_OF_SUBROUTINE_END


!===============================================================================
! 0 - GESTION MEMOIRE
!===============================================================================

idebia = idbia0
idebra = idbra0

! Indicateur d'arret (pour savoir si des faces ont ete oubliees)
iok = 0

!===============================================================================
!   COEFFICIENT D'ABSORPTION DU MILIEU (m-1)

!     DANS LE CAS DES PHYSIQUES PARTICULIERES (COMBUSTION GAZ/CHARBON/ELEC/FIOUL)

!         CK NE DOIT PAS ETRE FOURNI
       !==========
!         (il est determine automatiquement, eventuellement a partir
!          du fichier parametrique)

!     DANS LES AUTRES CAS
!         CK DOIT ETRE COMPLETE (IL EST NUL PAR DEFAUT)


!===============================================================================




if( ippmod(iphpar).le.1 ) then

  do iel = 1, ncel
    ck(iel) = 0.d0
  enddo

!--> MODELE P1 : Controle standard des valeurs du coefficient
!                d'absorption. Ce coefficient doit assurer une
!                longueur optique au minimum de l'ordre de l'unite.

  if (iirayo.eq.2) then
    sf = 0.d0
    vv = 0.d0

!         Calcul de la longueur caractéristique du domaine de calcul

    do ifac = 1,nfabor
      sf = sf + sqrt(                                             &
                surfbo(1,ifac)**2 +                               &
                surfbo(2,ifac)**2 +                               &
                surfbo(3,ifac)**2 )
    enddo
    if (irangp.ge.0) then
      call parsom(sf)
      !==========
    endif

    do iel = 1,ncel
      vv = vv + volume(iel)
    enddo
    if (irangp.ge.0) then
      call parsom(vv)
      !==========
    endif

    xlc = 3.6d0 * vv / sf

!         Clipping pour la variable CK

    xkmin = 1.d0 / xlc

    iok = 0

    do iel = 1,ncel
      if (ck(iel).lt.xkmin) then
        iok = iok + 1
      endif
    enddo

!     Arret en fin de pas de temps si epaisseur optique trop grande
!       (ISTPP1 = 1 permet d'arreter proprement a la fin du pas de temps
!        courant).
    pp = xnp1mx/100.0d0
    if (dble(iok).gt.pp*dble(ncel)) then
      write(nfecra,3000) xkmin, dble(iok)/dble(ncel)*100.d0,      &
                         xnp1mx
      istpp1 = 1
!            CALL CSEXIT (1)
       !==========
    endif
  endif

endif
! -------
! FORMATS
! -------

 3000 format(                                                           &
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/,&
'@ @@ ATTENTION : RAYONNEMENT APPROXIMATION P-1 (USRAY3)      ',/,&
'@    =========                                               ',/,&
'@                                                            ',/,&
'@    LA LONGUEUR OPTIQUE DU MILIEU SEMI-TRANSPARENT          ',/,&
'@      DOIT AU MOINS ETRE DE L''ORDRE DE L''UNITE POUR ETRE  ',/,&
'@      DANS LE DOMAINE D''APPLICATION DE L''APPROXIMATION P-1',/,&
'@    CELA NE SEMBLE PAS ETRE LE CAS ICI.                     ',/,&
'@                                                            ',/,&
'@    LE COEFFICIENT D''ABSORPTION MINIMUM POUR ASSURER CETTE ',/,&
'@      LONGUEUR OPTIQUE EST XKMIN = ',E10.4                   ,/,&
'@    CETTE VALEUR N''EST PAS ATTEINTE POUR ', E10.4,'%       ',/,&
'@      DES CELLULES DU MAILLAGE.                             ',/,&
'@    LE POURCENTAGE DE CELLULES DU MAILLAGE POUR LESQUELLES  ',/,&
'@      ON ADMET QUE CETTE CONDITION SOIT VIOLEE EST IMPOSE   ',/,&
'@      PAR DEFAUT OU DANS USINI1 A XNP1MX = ', E10.4,'%      ',/,&
'@                                                            ',/,&
'@    Le calcul est interrompu.                               ',/,&
'@                                                            ',/,&
'@    Verifier les valeurs du coefficient d''absorption CK    ',/,&
'@      dans PPCABS, USRAY3 ou Fichier thermochimie.          ',/,&
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/)


end subroutine
