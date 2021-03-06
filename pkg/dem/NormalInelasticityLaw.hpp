/*************************************************************************
*  Copyright (C) 2008 by Jérôme DURIEZ                                   *
*  duriez@geo.hmg.inpg.fr                                                *
*                                                                        *
*  This program is free software; it is licensed under the terms of the  *
*  GNU General Public License v2 or later. See file LICENSE for details. *
*************************************************************************/

#pragma once

#include<yade/pkg/common/Dispatching.hpp>
#include<yade/pkg/dem/ScGeom.hpp>
#include<yade/pkg/dem/NormalInelasticityPhys.hpp>
#include <set>
#include <boost/tuple/tuple.hpp>



class Law2_ScGeom6D_NormalInelasticityPhys_NormalInelasticity : public LawFunctor
{
	private :
		Vector3r moment // the part of the contact torque of the interaction due to relative rotations (a first part is due to contact forces)
			,f// contact force
			;
		Real Fn	 // value of normal force in the interaction
		    ,Fs // shear force
		    ,maxFs; // maximum value of shear force according to Coulomb-like criterion
		Real un;	 // value of interpenetration in the interaction
	public :
		virtual void go(shared_ptr<IGeom>&, shared_ptr<IPhys>&, Interaction*);

	FUNCTOR2D(ScGeom,NormalInelasticityPhys);

	YADE_CLASS_BASE_DOC_ATTRS_CTOR(Law2_ScGeom6D_NormalInelasticityPhys_NormalInelasticity,
				LawFunctor,
				"Contact law used to simulate granular filler in rock joints [Duriez2009a]_, [Duriez2011]_. It includes possibility of cohesion, moment transfer and inelastic compression behaviour (to reproduce the normal inelasticity observed for rock joints, for the latter).\n\n The moment transfer relation corresponds to the adaptation of the work of Plassiard & Belheine (see in [DeghmReport2006]_ for example), which was realized by J. Kozicki, and is now coded in :yref:`ScGeom6D`.\n\n As others :yref:`LawFunctor`, it uses pre-computed data of the interactions (rigidities, friction angles -with their tan()-, orientations of the interactions); this work is done here in :yref:`Ip2_2xNormalInelasticMat_NormalInelasticityPhys`.\n\n To use this you should also use :yref:`NormalInelasticMat` as material type of the bodies.\n\n The effects of this law are illustrated in examples/normalInelasticityTest.py",
				((bool,momentRotationLaw,true,,"boolean, true=> computation of a torque (against relative rotation) exchanged between particles"))
				((bool,momentAlwaysElastic,false,,"boolean, true=> the part of the contact torque (caused by relative rotations, which is computed only if momentRotationLaw..) is not limited by a plastic threshold"))
				,
				moment=Vector3r::Zero();
				f=Vector3r::Zero();
				Fn=0.0;
				Fs=0.0;
				maxFs=0.0;
				un=0.0;
				);
	
};

REGISTER_SERIALIZABLE(Law2_ScGeom6D_NormalInelasticityPhys_NormalInelasticity);

