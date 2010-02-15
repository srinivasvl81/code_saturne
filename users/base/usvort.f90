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

subroutine usvort &
!================

 ( idbia0 , idbra0 ,                                              &
   ndim   , ncelet , ncel   , nfac   , nfabor , nfml   , nprfml , &
   nnod   , lndfac , lndfbr , ncelbr ,                            &
   nvar   , nscal  , nphas  ,                                     &
   nideve , nrdeve , nituse , nrtuse ,                            &
   iphas  , iappel ,                                              &
   ifacel , ifabor , ifmfbr , ifmcel , iprfml , maxelt , lstelt , &
   ipnfac , nodfac , ipnfbr , nodfbr , irepvo ,                   &
   idevel , ituser , ia     ,                                     &
   xyzcen , surfac , surfbo , cdgfac , cdgfbo , xyznod , volume , &
   dt     , rtpa   , propce , propfa , propfb ,                   &
   coefa  , coefb  ,                                              &
   rdevel , rtuser , ra     )

!===============================================================================
! FONCTION :
! --------

! METHODE DES VORTEX POUR LES CONDITIONS AUX LIMITES D'ENTREE
!  EN L.E.S. :
!  DEFINITION DES ENTREES AVEC VORTEX
!  DEFINITION DES CARACTERISTIQUES DES VORTEX


! Boundary faces identification
! =============================

! Boundary faces may be identified using the 'getfbr' subroutine.
! The syntax of this subroutine is described in the 'usclim' subroutine,
! but a more thorough description can be found in the user guide.


!-------------------------------------------------------------------------------
! Arguments
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
! nphas            ! i  ! <-- ! number of phases                               !
! nideve, nrdeve   ! i  ! <-- ! sizes of idevel and rdevel arrays              !
! nituse, nrtuse   ! i  ! <-- ! sizes of ituser and rtuser arrays              !
! iphas            ! e  ! <-- ! numero de la phase                             !
! iappel           ! e  ! <-- ! indique les donnes a renvoyer                  !
! ifacel(2, nfac)  ! ia ! <-- ! interior faces -> cells connectivity           !
! ifabor(nfabor)   ! ia ! <-- ! boundary faces -> cells connectivity           !
! ifmfbr(nfabor)   ! ia ! <-- ! boundary face family numbers                   !
! ifmcel(ncelet)   ! ia ! <-- ! cell family numbers                            !
! iprfml           ! ia ! <-- ! property numbers per family                    !
!  (nfml, nprfml)  !    !     !                                                !
! maxelt           ! i  ! <-- ! max number of cells and faces (int/boundary)   !
! lstelt(maxelt)   ! ia ! --- ! work array                                     !
! ipnfac(nfac+1)   ! ia ! <-- ! interior faces -> vertices index (optional)    !
! nodfac(lndfac)   ! ia ! <-- ! interior faces -> vertices list (optional)     !
! ipnfbr(nfabor+1) ! ia ! <-- ! boundary faces -> vertices index (optional)    !
! nodfbr(lndfbr)   ! ia ! <-- ! boundary faces -> vertices list (optional)     !
! irepvo           ! te ! <-- ! numero de l'entree associe a chaque            !
!     (nfabor)     !    !     ! face de bord (=0 si pas de vortex)             !
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
! coefa, coefb     ! ra ! <-- ! boundary conditions                            !
!  (nfabor, *)     !    !     !                                                !
! rdevel(nrdeve)   ! ra ! <-> ! real work array for temporary development      !
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
include "optcal.h"
include "entsor.h"
include "vortex.h"

!===============================================================================

! Arguments

integer          idbia0 , idbra0
integer          ndim   , ncelet , ncel   , nfac   , nfabor
integer          nfml   , nprfml
integer          nnod   , lndfac , lndfbr , ncelbr
integer          nvar   , nscal  , nphas
integer          nideve , nrdeve , nituse , nrtuse
integer          iphas  , iappel

integer          ifacel(2,nfac) , ifabor(nfabor)
integer          ifmfbr(nfabor) , ifmcel(ncelet)
integer          iprfml(nfml,nprfml)
integer          maxelt, lstelt(maxelt)
integer          ipnfac(nfac+1), nodfac(lndfac)
integer          ipnfbr(nfabor+1), nodfbr(lndfbr)
integer          irepvo(nfabor)
integer          idevel(nideve), ituser(nituse), ia(*)

double precision xyzcen(ndim,ncelet)
double precision surfac(ndim,nfac), surfbo(ndim,nfabor)
double precision cdgfac(ndim,nfac), cdgfbo(ndim,nfabor)
double precision xyznod(ndim,nnod), volume(ncelet)
double precision dt(ncelet), rtpa(ncelet,*)
double precision propce(ncelet,*)
double precision propfa(nfac,*), propfb(nfabor,*)
double precision coefa(nfabor,*), coefb(nfabor,*)
double precision rdevel(nrdeve), rtuser(nrtuse), ra(*)

! Local variables

integer          ifac, ient
integer          ilelt, nlelt

!===============================================================================

! TEST_TO_REMOVE_FOR_USE_OF_SUBROUTINE_START
!===============================================================================

if(1.eq.1) return

!===============================================================================
! TEST_TO_REMOVE_FOR_USE_OF_SUBROUTINE_END


!===============================================================================
! 1. PARAMETRES GLOBAUX
!===============================================================================

! --- Nombre d'entrees avec la methode des vortex

nnent = 2

! --- Nombre de vortex a mettre dans chaque entree

!   NVORT min ~ Surface d'entree/(pi*SIGMA**2)

nvort(1) = 500
nvort(2) = 500

if (iappel.eq.1) then

!===============================================================================
! 2. DEFINITION DES ZONES D'ENTREE (AU PREMIER PASSAGE)
!===============================================================================

  do ifac = 1, nfabor
    irepvo(ifac) = 0
  enddo

! ------------------
!   ENTREE 1
! ------------------
  CALL GETFBR('3',NLELT,LSTELT)
  !==========

  do ilelt = 1, nlelt

    ifac = lstelt(ilelt)

    ient = 1
    irepvo(ifac) = ient

  enddo

! ------------------
!   ENTREE 2
! ------------------
  CALL GETFBR('1',NLELT,LSTELT)
  !==========

  do ilelt = 1, nlelt

    ifac = lstelt(ilelt)

    ient = 2
    irepvo(ifac) = ient

  enddo

elseif (iappel.eq.2) then

!===============================================================================
! 3. PARAMETRES GEOMETRIQUES ET CONDITIONS LIMITES
!===============================================================================

! --- Cas trait�

! ICAS = 1...Conduite rectangulaire
!        2...Conduite circulaire
!        3...Geometrie quelconque sans traitement specifique des conditions aux limites
!        4...Geometrie quelconque sans traitement specifique des conditions aux limites
!            ni fichier de donnees (la vitesse moyenne, le niveau de k et de epsilon
!            sont fournis par l'utilisateur)

  ient = 1
  icas(ient) = 1

  ient = 2
  icas(ient) = 2


! --- Repere definissant le plan d'entree

!     Si ICAS = 4, le code se charge de ces donnees
!     Sinon il faut preciser les vecteurs DIR1 et DIR2 definissant
!     un rep�re directe tel que DIR3 soit un vecteur entrant normal
!     a la face d'entree.

  ient = 1
  if(icas(ient).eq.1.or.icas(ient).eq.2.or.icas(ient).eq.3) then
    dir1(1,ient) = 1.d0
    dir1(2,ient) = 0.d0
    dir1(3,ient) = 0.d0

    dir2(1,ient) = 0.d0
    dir2(2,ient) = 1.d0
    dir2(3,ient) = 0.d0
  endif

  ient = 2
  if(icas(ient).eq.1.or.icas(ient).eq.2.or.icas(ient).eq.3) then
    dir1(1,ient) = 0.d0
    dir1(2,ient) = 1.d0
    dir1(3,ient) = 0.d0

    dir2(1,ient) = 0.d0
    dir2(2,ient) = 0.d0
    dir2(3,ient) = 1.d0
  endif

! --- Centre du repere local dans le plan d'entree

!     Si ICAS = 1 ou ICAS = 2, le centre du repere doit correspondre
!                 au centre de gravite de la zone d'entree (rectangle ou cercle)

  ient = 1

  cen(1,ient) = 0.d0
  cen(2,ient) = 0.d0
  cen(3,ient) = -6.05d-1

  ient = 2

  cen(1,ient) = -3.664d-1
  cen(2,ient) = 0.d0
  cen(3,ient) = 0.d0

! --- Condition aux limites

! -> Si ICAS = 1...Il faut specifier le type de condition aux limite ICLVOR
!               dans les directions DIR1, DIR2, - DIR1, -DIR2

!               Ces conditions peuvent etre de 3 types :

! ICLVOR = 1...Condition de paroi
!          2...Condition de symetrie
!          3...Condition de periodicite

!                    y = LLY/2
!                    (ICLVOR 1)
!           +-----------------------+
!           |           ^ DIR1      |
!           |           |           |
!           |           |           |
! z=- LLZ/2 |           +----> DIR2 | z = LLZ/2
! (ICLVOR 4)|                       | (ICLVOR 2)
!           |                       |
!           |                       |
!           +-----------------------+
!                    y = -LLY/2
!                    (ICLVOR 3)


! -> Si ICAS = 2, les conditions sont necessairement de type paroi
! -> Si ICAS = 3 ou 4, pas de traitement particulier

  ient = 1

  if(icas(ient).eq.1) then
    iclvor(1,ient) = 1
    iclvor(2,ient) = 2
    iclvor(3,ient) = 1
    iclvor(4,ient) = 2
  endif

! LLY et LLZ sont les dimensions de l'entree dans les directions DIR1 et DIR2
! LDD est le diametre de la conduite


  ient = 1
  lly(ient) = 0.2d0
  llz(ient) = 0.1d0

  ient = 2
  lld(2) = 0.154d0

!===============================================================================
! 5. PARAMETRES PHYSIQUES ET MARCHE EN TEMPS
!===============================================================================

! --- " Temps de vie " limite du vortex

! ITLIVO = 1...Les vortex sont retire au bout du temps TLIMVO
!                donne par l'utilisateur
!                ( par exemple TLIMVO = 10*DTREF)

!          2...Chaque vortex a un temps d'exitence limite valant
!                5.Cmu.k^(3/2).U/epsilon
!               ( ou U est la vitesse principale suivant DIR3)

  ient = 1
  itlivo(ient) = 1

  if(itlivo(ient).eq.1) then
    tlimvo(ient) = 10.d0*dtref
  endif

  ient = 2
  itlivo(ient) = 2


! --- " Diametre " des vortex

! ISGMVO = 1...diametre constant XSGMVO donne par l'utilisateur
!          2...basee sur la formule sigma = Cmu^(3/4).k^(3/2)/epsilon
!          3...basee sur la formule sigma = max(Lt, Lk) avec
!                 Lt = (5 nu.k/epsilon)^(1/2)
!             et  Lk = 200.(nu^3/epsilon)^(1/4)

  ient = 1
  isgmvo(ient) = 1

  if(isgmvo(ient).eq.1) then
    xsgmvo(ient) = 0.01d0
  endif

  ient = 2
  isgmvo(ient) = 2


! --- Mode de deplacement des vortex

! IDEPVO = 1...Deplacement en r*UD (r aleatoire dans [0,1])
!              UD a fournir par l'utilisateur
!          2...Convection par les vortex

  ient = 1
  idepvo(ient) = 2

  ient = 2
  idepvo(ient) = 1

  if(idepvo(ient).eq.1) then
    ud(ient) = 0.7d0
  endif

!===============================================================================
! 6. PARAMETRES D'ENTREE / SORTIES ET DONNEES UTILISATEUR
!===============================================================================

! --- Fichier de donnees utilisateur

! NDAT ...Nombre de lignes du fichier de donnees contenant les donnees :
!          x | y | z | U | V | W | Grad[u.DIR3].n | k | epsilon

!         dans le plan d'entree du calcul

!         Grad[u.DIR3].n est le gradient dans la direction normale
!         a la paroi, de la vitesse principale dans le plan d'entree.
!         Cette donn�es n'est utilis�e qu'avec ICAS=2

! FICVOR...Nom du fichier de donnees utilisateur

  ient = 1
  ndat(ient) = 2080

  ient = 2
  ndat(ient) = 2080

! Par les defaut les fichiers sont nommes "vordat" affect� de l'indice
! d'entr�e

  ient = 1
  FICVOR(IENT) = 'entree_1.dat'

  ient = 2
  FICVOR(IENT) = 'entree_2.dat'

! Pour ICAS = 4, on precise juste la valeur moyenne de U, k et de espilon
! a l'entree

  if(icas(ient).eq.4) then
    udebit(ient) = 10.d0
    kdebit(ient) = 1.d0
    edebit(ient) = 1.d0
  endif

! --- Relecture d'un fichier suite eventuel

! ISUIVO = 0...Pas de relecture (reinitialisation des vortex)
!          1...Relecture du fichier suite de methode des vortex

  isuivo = isuite


endif


return
end subroutine

!===============================================================================
! 7. DEFINTION DE LA FONCTION PERMETAT D'IMPOSER LES DONNEES D'ENTREE
!===============================================================================

function phidat &
!==============

 ( nfecra , icas   , ndat   ,                                     &
   yy     , zz     , ydat   , zdat   ,                            &
   vardat , iii    )

!===============================================================================
! FONCTION :
! --------

! FONCTION PERMETTANT D'INTERPOLER LES DONNEES D'ENTREE FOURNIES
! PAR L'UTILISATEUR AU CENTRE DES FACES D'ENTREE POUR LESQUELLES
! EST UTILISEE LA METHODE DES VORTEX

!-------------------------------------------------------------------------------
! Arguments
!__________________.____._____.________________________________________________.
! name             !type!mode ! role                                           !
!__________________!____!_____!________________________________________________!
! nfecra           ! e  ! <-- ! unite                                          !
! icas             ! e  ! <-- ! type de geometrie du cas                       !
! ndat             ! e  ! <-- ! nbr de lignes du fichier de donnees            !
! yy               ! e  ! <-- ! coordoonnes dans le repere local du            !
! zz               ! e  ! <-- ! point ou l'on cherche a connaitre la           !
!                  !    !     ! variable vardat                                !
! ydat             ! e  ! <-- ! coordoonnes ou est connue la variable          !
! zdat             ! e  ! <-- ! vardat dans le fichier de donnees              !
! vardat           ! e  ! <-- ! valeur de la variable vardat                   !
! iii              ! e  ! --> ! ligne ou a ete trouvee la donnee la            !
!                  !    !     ! plus proche du point (yy,zz)                   !
!__________________!____!_____!________________________________________________!

!     Type: i (integer), r (real), s (string), a (array), l (logical),
!           and composite types (ex: ra real array)
!     mode: <-- input, --> output, <-> modifies data, --- work array
!===============================================================================

implicit none

integer          nfecra, icas, ndat, iii
double precision zz, yy
double precision zdat(ndat), ydat(ndat)
double precision vardat(ndat)

integer          ii
double precision phidat, dist1


! Dans l'exemple suivant, on se contente de retourne la valeur situee
! dans le fichier de donnee a l'abscisse la plus proche du point de
! coordonn�e (Y,Z) ou l'on cherche a connaitre la valeur de la
! variable numero VARDAT.


if(icas.eq.1.or.icas.eq.2.or.icas.eq.3) then

  if(iii.eq.0) then
    dist1 = 1.d20
    do ii = 1,ndat
      if(sqrt((yy-ydat(ii))**2+(zz-zdat(ii))**2).lt.dist1) then
        dist1 = sqrt((zz-zdat(ii))**2+(yy-ydat(ii))**2)
        iii   = ii
        phidat = vardat(ii)
      endif
    enddo
  elseif(iii.ne.0) then
    phidat =  vardat(iii)
  endif

elseif(icas.eq.4) then
  phidat = vardat(1)
endif

return
end function
