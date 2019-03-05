/*
 * TestA.cpp
 *
 *  Created on: 27.02.2019
 *      Author: helmo
 */

#include "generated/MockA.hpp"

#include "gmock/gmock.h"

TEST(TestA, createTest)
{
	auto mock = NA::NAA::MockA::create();
	auto strictMock = NA::NAA::MockA::createStrict();
	EXPECT_NE(nullptr, mock);
	EXPECT_NE(nullptr, strictMock);
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
