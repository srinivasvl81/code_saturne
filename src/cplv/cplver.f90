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

subroutine cplver &
!================

 ( iok    )

!===============================================================================
!  FONCTION  :
!  ---------

!   SOUS-PROGRAMME DU MODULE LAGRANGIEN COUPLE CHARBON PULVERISE :
!   --------------------------------------------------------------

!      COMBUSTION EULERIENNE DE CHARBON PULVERISE ET
!      TRANSPORT LAGRANGIEN DES PARTICULES DE CHARBON

!      VERIFICATION DES PARAMETRES DE CALCUL
!        APRES INTERVENTION UTILISATEUR
!        (COMMONS)
!-------------------------------------------------------------------------------
! Arguments
!__________________.____._____.________________________________________________.
! name             !type!mode ! role                                           !
!__________________!____!_____!________________________________________________!
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
include "cpincl.h"
include "ppincl.h"

!===============================================================================

! Arguments

integer          iok

! Local variables

character        chaine*80
integer          ipp, isc, jj, iphas
integer          ige

!===============================================================================

!===============================================================================
! 1. OPTIONS DU CALCUL : TABLEAUX DE ppincl.h : formats 2000
!===============================================================================

! --> Coefficient de relaxation de la masse volumique

if( srrom.lt.0d0 .or. srrom.gt.1d0) then
  WRITE(NFECRA,2000)'SRROM ', SRROM
  iok = iok + 1
endif

!===============================================================================
! 2. TABLEAUX DE cstphy.h et ppthch.F : formats 3000
!===============================================================================

iphas = 1

! --> Masse volumique

if( ro0(iphas).lt.0d0) then
    WRITE(NFECRA,3000)IPHAS,'RO0   ', RO0(IPHAS)
    iok = iok + 1
  endif

! --> Diffusivite dynamique en kg/(m s) : DIFTL0

if( diftl0.lt.0d0) then
  WRITE(NFECRA,3010)'DIFTL0', DIFTL0
  iok = iok + 1
else
  visls0(ihm) = diftl0
endif

!===============================================================================
! 3. FORMATS VERIFICATION
!===============================================================================

 2000 format(                                                           &
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/,&
'@ @@ ATTENTION : ARRET A L''ENTREE DES DONNEES               ',/,&
'@    =========                                               ',/,&
'@    PHYSIQUE PARTICULIERE (C.P. COUPLE LAGRANGIEN)          ',/,&
'@                                                            ',/,&
'@    ',A6,                            ' DOIT ETRE UN REEL    ',/,&
'@    COMPRIS ENTRE 0 ET 1                                    ',/,&
'@    IL VAUT ICI ',E14.5                                      ,/,&
'@                                                            ',/,&
'@  Le calcul ne peut etre execute.                           ',/,&
'@                                                            ',/,&
'@  Verifier uscpi1.                                          ',/,&
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/)
 3000 format(                                                           &
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/,&
'@ @@ ATTENTION : ARRET A L''ENTREE DES DONNEES               ',/,&
'@    =========                                               ',/,&
'@    PHYSIQUE PARTICULIERE (C.P. COUPLE LAGRANGIEN)          ',/,&
'@                                                            ',/,&
'@    PHASE ',I10                                              ,/,&
'@    ',A6,' DOIT ETRE UN REEL POSITIF                        ',/,&
'@    IL VAUT ICI ',E14.5                                      ,/,&
'@                                                            ',/,&
'@  Le calcul ne peut etre execute.                           ',/,&
'@                                                            ',/,&
'@  Verifier uscpi1.                                          ',/,&
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/)
 3010 format(                                                           &
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/,&
'@ @@ ATTENTION : ARRET A L''ENTREE DES DONNEES               ',/,&
'@    =========                                               ',/,&
'@    PHYSIQUE PARTICULIERE (C.P. COUPLE LAGRANGIEN)          ',/,&
'@                                                            ',/,&
'@    ',A6,' DOIT ETRE UN REEL POSITIF                        ',/,&
'@    IL VAUT ICI ',E14.5                                      ,/,&
'@                                                            ',/,&
'@  Le calcul ne peut etre execute.                           ',/,&
'@                                                            ',/,&
'@  Verifier uscpi1.                                          ',/,&
'@                                                            ',/,&
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',/,&
'@                                                            ',/)

!===============================================================================
! 4. SORTIE
!===============================================================================

return
end subroutine
