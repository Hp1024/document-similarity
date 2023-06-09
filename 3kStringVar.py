"""Module for testing string variables."""

class TestStringVar(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            stringCol = "String %d" % i
            fixedCharCol = ("Fixed Char %d" % i).ljust(40)
            rawCol = ("Raw %d" % i).encode("ascii")
            if i % 2:
                nullableCol = "Nullable %d" % i
            else:
                nullableCol = None
            dataTuple = (i, stringCol, rawCol, fixedCharCol, nullableCol)
            self.rawData.append(dataTuple)
            self.dataByKey[i] = dataTuple

    def testBindString(self):
        "test binding in a string"
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :p_Value""",
                p_Value = "String 5")
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindDifferentVar(self):
        "test binding a different variable on second execution"
        retval_1 = self.cursor.var(cx_Oracle.STRING, 30)
        retval_2 = self.cursor.var(cx_Oracle.STRING, 30)
        self.cursor.execute("begin :retval := 'Called'; end;",
                retval = retval_1)
        self.failUnlessEqual(retval_1.getvalue(), "Called")
        self.cursor.execute("begin :retval := 'Called'; end;",
                retval = retval_2)
        self.failUnlessEqual(retval_2.getvalue(), "Called")

    def testBindStringAfterNumber(self):
        "test binding in a string after setting input sizes to a number"
        self.cursor.setinputsizes(p_Value = cx_Oracle.NUMBER)
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :p_Value""",
                p_Value = "String 6")
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[6]])

    def testBindStringArrayDirect(self):
        "test binding in a string array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        statement = """
                begin
                  :p_ReturnValue := pkg_TestStringArrays.TestInArrays(
                      :p_IntegerValue, :p_Array);
                end;"""
        self.cursor.execute(statement,
                p_ReturnValue = returnValue,
                p_IntegerValue = 5,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 86)
        array = [ "String - %d" % i for i in range(15) ]
        self.cursor.execute(statement,
                p_IntegerValue = 8,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 163)

    def testBindStringArrayBySizes(self):
        "test binding in a string array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(p_Array = [cx_Oracle.STRING, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute("""
                begin
                  :p_ReturnValue := pkg_TestStringArrays.TestInArrays(
                      :p_IntegerValue, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_IntegerValue = 6,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 87)

    def testBindStringArrayByVar(self):
        "test binding in a string array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.STRING, 10, 20)
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute("""
                begin
                  :p_ReturnValue := pkg_TestStringArrays.TestInArrays(
                      :p_IntegerValue, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_IntegerValue = 7,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 88)

    def testBindInOutStringArrayByVar(self):
        "test binding in/out a string array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.STRING, 10, 100)
        originalData = [r[1] for r in self.rawData]
        expectedData = ["Converted element # %d originally had length %d" % \
                (i, len(originalData[i - 1])) for i in range(1, 6)] + \
                originalData[5:]
        array.setvalue(0, originalData)
        self.cursor.execute("""
                begin
                  pkg_TestStringArrays.TestInOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 5,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(), expectedData)

    def testBindOutStringArrayByVar(self):
        "test binding out a string array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.STRING, 6, 100)
        expectedData = ["Test out element # %d" % i for i in range(1, 7)]
        self.cursor.execute("""
                begin
                  pkg_TestStringArrays.TestOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 6,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(), expectedData)

    def testBindRaw(self):
        "test binding in a raw"
        self.cursor.setinputsizes(p_Value = cx_Oracle.BINARY)
        self.cursor.execute("""
                select * from TestStrings
                where RawCol = :p_Value""",
                p_Value = b"Raw 4")
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindAndFetchRowid(self):
        "test binding (and fetching) a rowid"
        self.cursor.execute("""
                select rowid
                from TestStrings
                where IntCol = 3""")
        rowid, = self.cursor.fetchone()
        self.cursor.execute("""
                select *
                from TestStrings
                where rowid = :p_Value""",
                p_Value = rowid)
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[3]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :p_Value""",
                p_Value = None)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testBindOutSetInputSizesByType(self):
        "test binding out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(p_Value = cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :p_Value := 'TSI';
                end;""")
        self.failUnlessEqual(vars["p_Value"].getvalue(), "TSI")

    def testBindOutSetInputSizesByInteger(self):
        "test binding out with set input sizes defined (by integer)"
        vars = self.cursor.setinputsizes(p_Value = 30)
        self.cursor.execute("""
                begin
                  :p_Value := 'TSI (I)';
                end;""")
        self.failUnlessEqual(vars["p_Value"].getvalue(), "TSI (I)")

    def testBindInOutSetInputSizesByType(self):
        "test binding in/out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(p_Value = cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :p_Value := :p_Value || ' TSI';
                end;""",
                p_Value = "InVal")
        self.failUnlessEqual(vars["p_Value"].getvalue(), "InVal TSI")

    def testBindInOutSetInputSizesByInteger(self):
        "test binding in/out with set input sizes defined (by integer)"
        vars = self.cursor.setinputsizes(p_Value = 30)
        self.cursor.execute("""
                begin
                  :p_Value := :p_Value || ' TSI (I)';
                end;""",
                p_Value = "InVal")
        self.failUnlessEqual(vars["p_Value"].getvalue(), "InVal TSI (I)")

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :p_Value := 'TSI (VAR)';
                end;""",
                p_Value = var)
        self.failUnlessEqual(var.getvalue(), "TSI (VAR)")

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.STRING)
        var.setvalue(0, "InVal")
        self.cursor.execute("""
                begin
                  :p_Value := :p_Value || ' TSI (VAR)';
                end;""",
                p_Value = var)
        self.failUnlessEqual(var.getvalue(), "InVal TSI (VAR)")

    def testBindLongString(self):
        "test that binding a long string succeeds"
        self.cursor.execute("""
                declare
                  t_Temp varchar2(10000);
                begin
                  t_Temp := :bigString;
                end;""",
                bigString = "X" * 10000)

    def testBindLongStringAfterSettingSize(self):
        "test that setinputsizes() returns a long variable"
        var = self.cursor.setinputsizes(test = 90000)["test"]
        self.failUnlessEqual(type(var), cx_Oracle.LONG_STRING)
        inString = "1234567890" * 9000
        var.setvalue(0, inString)
        outString = var.getvalue()
        self.failUnlessEqual(inString, outString,
                "output does not match: in was %d, out was %d" % \
                (len(inString), len(outString)))

    def testStringMaximumReached(self):
        "test that an error is raised when maximum string length exceeded"
        var = self.cursor.setinputsizes(test = 100)["test"]
        inString = "1234567890" * 400
        var.setvalue(0, inString)
        outString = var.getvalue()
        self.failUnlessEqual(inString, outString,
                "output does not match: in was %d, out was %d" % \
                (len(inString), len(outString)))
        badStringSize = 4000 * self.connection.maxBytesPerCharacter + 1
        inString = "X" * badStringSize
        self.failUnlessRaises(ValueError, var.setvalue, 0, inString)

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestStrings")
        self.failUnlessEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  ('STRINGCOL', cx_Oracle.STRING, 20, 20, 0, 0, 0),
                  ('RAWCOL', cx_Oracle.BINARY, 30, 30, 0, 0, 0),
                  ('FIXEDCHARCOL', cx_Oracle.FIXED_CHAR, 40, 40, 0, 0, 0),
                  ('NULLABLECOL', cx_Oracle.STRING, 50, 50, 0, 0, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestStrings order by IntCol")
        self.failUnlessEqual(self.cursor.fetchall(), self.rawData)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestStrings order by IntCol")
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.failUnlessEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.failUnlessEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.failUnlessEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestStrings
                where IntCol in (3, 4)
                order by IntCol""")
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.failUnlessEqual(self.cursor.fetchone(), None)

