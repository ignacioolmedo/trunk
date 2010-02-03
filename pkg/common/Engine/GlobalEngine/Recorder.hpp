// 2009 © Václav Šmilauer <eudoxos@arcig.cz>
#pragma once 
#include<yade/pkg-common/PeriodicEngines.hpp>
#include<fstream>
#include<string>
class Recorder: public PeriodicEngine{
	void openAndCheck();
	protected:
		//! stream object that derived engines should write to
		std::ofstream out;
	public:
		virtual ~Recorder(); // vtable
		virtual bool isActivated(Scene* rb){
			if(PeriodicEngine::isActivated(rb)){
				if(!out.is_open()) openAndCheck();
				return true;
			}
			return false;
		}
	YADE_CLASS_BASE_DOC_ATTRDECL_CTOR_PY(Recorder,PeriodicEngine,"Engine periodically storing some data to (one) external file. In addition PeriodicEngine, it handles opening the file as needed. See :yref:`PeriodicEngine` for controlling periodicity.",
		((std::string,file,,"Name of file to save to; must not be empty."))
		((bool,truncate,false,"Whether to delete current file contents, if any, when opening (false by default)"))
		,,
	);
};
REGISTER_SERIALIZABLE(Recorder);
