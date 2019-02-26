#ifndef I2_HPP
#define I2_HPP

#include <memory>
#include <functional>
#include <string>

namespace n1 {

class I2
{
public:
    virtual ~I2();

    virtual void f0()const=0;

    virtual void f1(
        int
    ) = 0;

    virtual void f2(double) = 0;
    virtual void f3(int, double) = 0;
    virtual void f4(int i, double d, const std::string& str) = 0;
    virtual int f5(const std::string& str) = 0;
    virtual std::shared_ptr<int> f6(const std::shared_ptr<int>&) const = 0;
    virtual const int& f7() const = 0;
    virtual std::function<void(int)> f8() = 0;
    virtual const int * const f10() = 0;

    inline virtual const void f11() = 0;
    virtual inline const void f12() = 0;
    virtual const void f13() = 0;
    const virtual void f14() = 0;
    volatile const virtual void f15() = 0;
    const virtual volatile void f16() = 0;
    const virtual volatile inline void f17() = 0;

    virtual int operator()() = 0;
    virtual void operator()(int, double d, std::function<void(int, double)>, const int&, const std::string& str) = 0;
    virtual double operator[](int) = 0;
    virtual void* operator->() const = 0;
};

} // namespace n1

#endif

