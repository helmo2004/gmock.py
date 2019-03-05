#include "C.hpp"

namespace NB {
class B :  public virtual C
{
public:
	virtual ~B() {}
	virtual void Bbb() = 0;
	virtual int Abc() = 0;
};
}
