/*
 * TestA.cpp
 *
 *  Created on: 27.02.2019
 *      Author: helmo
 */

#include "generated/MockA.hpp"
#include "gmock/gmock.h"

using namespace testing;

#define CREATE_MOCKS(__CLASS__) \
	auto mock = __CLASS__::create(); \
	auto strictMock = __CLASS__::createStrict(); \
	EXPECT_NE(nullptr, mock); \
	EXPECT_NE(nullptr, strictMock);

#define TEST_MOCK_CALL_RESULT(__CLASS__, __CALL__, __RESULT__) \
{ \
	CREATE_MOCKS(__CLASS__); \
	EXPECT_CALL(*mock, __CALL__).WillOnce(Return(__RESULT__)); \
	EXPECT_EQ(__RESULT__, mock->__CALL__); \
	EXPECT_CALL(*strictMock, __CALL__).WillOnce(Return(__RESULT__)); \
	EXPECT_EQ(__RESULT__, strictMock->__CALL__); \
}

#define TEST_MOCK_CALL_NO_RESULT(__CLASS__, __CALL__) \
{ \
	CREATE_MOCKS(__CLASS__); \
	EXPECT_CALL(*mock, __CALL__); \
	mock->__CALL__; \
	EXPECT_CALL(*strictMock, __CALL__); \
	strictMock->__CALL__; \
}

TEST(TestA, MacroTest)
{
	TEST_MOCK_CALL_RESULT(NA::NAA::MockA, Abc(), 1);
	TEST_MOCK_CALL_NO_RESULT(NA::NAA::MockA, Aaa(3));
}

TEST(TestA, callTest)
{
	auto strictMock = NA::NAA::MockA::createStrict();
	EXPECT_CALL(*strictMock, Aaa(1));
	EXPECT_CALL(*strictMock, Bbb());
	EXPECT_CALL(*strictMock, Ccc());
	strictMock->Aaa(1);
	strictMock->Bbb();
	strictMock->Ccc();

	testing::Mock::VerifyAndClearExpectations(strictMock.get());

	// Check if Const Overload works
	const NA::NAA::MockA& constA = *strictMock.get();
	EXPECT_CALL(*strictMock, Ccc()).Times(0);
	EXPECT_CALL(constA, Ccc());
	constA.Ccc();
}
