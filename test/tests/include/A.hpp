#include "B.hpp"

namespace NA {
namespace NAA {

class A : public virtual NB::B
{
public:
	virtual void Aaa(int) = 0;
};

}
}
