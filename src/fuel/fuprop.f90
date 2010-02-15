!-------------------------------------------------------------------------------

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

subroutine fuprop &
!================

 ( ipropp , ipppst )

!===============================================================================
!  FONCTION  :
!  ---------

! INIT DES POSITIONS DES VARIABLES D'ETAT SELON
!         COMBUSTION FUEL
!   (DANS VECTEURS PROPCE, PROPFA, PROPFB)

!-------------------------------------------------------------------------------
! Arguments
!__________________.____._____.________________________________________________.
! name             !type!mode ! role                                           !
!__________________!____!_____!________________________________________________!
! ipropp           ! e  ! <-- ! numero de la derniere propriete                !
!                  !    !     !  (les proprietes sont dans propce,             !
!                  !    !     !   propfa ou prpfb)                             !
! ipppst           ! e  ! <-- ! pointeur indiquant le rang de la               !
!                  !    !     !  derniere grandeur definie aux                 !
!                  !    !     !  cellules (rtp,propce...) pour le              !
!                  !    !     !  post traitement                               !
!__________________!____!_____!________________________________________________!

!     TYPE : E (ENTIER), R (REEL), A (ALPHANUMERIQUE), T (TABLEAU)
!            L (LOGIQUE)   .. ET TYPES COMPOSES (EX : TR TABLEAU REEL)
!     MODE : <-- donnee, --> resultat, <-> Donnee modifiee
!            --- tableau de travail
!===============================================================================

implicit none

!===============================================================================
! Common blocks
!===============================================================================

include "paramx.h"
include "dimens.h"
include "numvar.h"
include "optcal.h"
include "cstphy.h"
include "entsor.h"
include "cstnum.h"
include "ppppar.h"
include "ppthch.h"
include "coincl.h"
include "ppcpfu.h"
include "cpincl.h"
include "fuincl.h"
include "ppincl.h"

!===============================================================================

! Arguments

integer       ipropp, ipppst

! Local variables

integer       iprop, ige , icla , iprop2

!===============================================================================

! ---> Definition des pointeurs relatifs aux variables d'etat

iprop = ipropp

!    Phase continue (melange gazeux)
iprop   = iprop + 1
itemp1  = iprop
iprop   = iprop + 1
irom1   = iprop
do ige = 1, ngaze
  iprop     = iprop +1
  iym1(ige) = iprop
enddo
iprop = iprop + 1
immel = iprop

if ( ieqnox .eq. 1 ) then
  iprop = iprop + 1
  ighcn1 = iprop
  iprop = iprop + 1
  ighcn2 = iprop
  iprop = iprop + 1
  ignoth = iprop
endif

!   Phase dispersee (classes de particules)

iprop2 = iprop
do icla = 1, nclafu
  iprop        = iprop2 + icla
  itemp3(icla) = iprop
  iprop        = iprop2 + 1*nclafu + icla
  irom3(icla)  = iprop
  iprop        = iprop2 + 2*nclafu + icla
  idiam3(icla) = iprop
  iprop        = iprop2 + 3*nclafu + icla
  ih1hlf(icla) = iprop
  iprop        = iprop2 + 4*nclafu + icla
  igmeva(icla) = iprop
  iprop        = iprop2 + 5*nclafu + icla
  igmhtf(icla) = iprop
enddo

! ---- Nb de variables algebriques (ou d'etat)
!         propre a la physique particuliere NSALPP
!         total NSALTO

nsalpp = iprop - ipropp
nsalto = iprop

! ----  On renvoie IPROPP au cas ou d'autres proprietes devraient
!         etre numerotees ensuite

ipropp = iprop

! ---> Positionnement dans le tableau PROPCE
!      et reperage du rang pour le post-traitement

iprop           = nproce

!    Phase continue (melange gazeux)
iprop           = iprop + 1
ipproc(itemp1)  = iprop
ipppst          = ipppst + 1
ipppro(iprop)   = ipppst

iprop           = iprop + 1
ipproc(irom1)   = iprop
ipppst          = ipppst + 1
ipppro(iprop)   = ipppst

do ige = 1, ngaze
  iprop              = iprop + 1
  ipproc(iym1(ige))  = iprop
  ipppst             = ipppst + 1
  ipppro(iprop)      = ipppst
enddo

iprop                 = iprop + 1
ipproc(immel)         = iprop
ipppst                = ipppst + 1
ipppro(iprop)         = ipppst

if ( ieqnox .eq. 1 ) then

  iprop                 = iprop + 1
  ipproc(ighcn1)        = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop + 1
  ipproc(ighcn2)        = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop + 1
  ipproc(ignoth)        = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

endif

!   Phase dispersee (classes de particules)

iprop2 = iprop
do icla = 1, nclafu

  iprop                 = iprop2 + icla
  ipproc(itemp3(icla))  = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop2 + 1*nclafu + icla
  ipproc(irom3(icla))   = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop2 + 2*nclafu + icla
  ipproc(idiam3(icla))  = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop2 + 3*nclafu + icla
  ipproc(ih1hlf(icla))  = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop2 + 4*nclafu + icla
  ipproc(igmeva(icla))  = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

  iprop                 = iprop2 + 5*nclafu + icla
  ipproc(igmhtf(icla))  = iprop
  ipppst                = ipppst + 1
  ipppro(iprop)         = ipppst

enddo


nproce = iprop


! ---> Positionnement dans le tableau PROPFB
!      Au centre des faces de bord

iprop  = nprofb
nprofb = iprop

! ---> Positionnement dans le tableau PROPFA
!      Au centre des faces internes (flux de masse)

iprop  = nprofa
nprofa = iprop

return
end subroutine
