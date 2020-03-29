USE [DataValidation]
GO

/****** Object:  StoredProcedure [dbo].[sp_GenerateDimCalendar]    Script Date: 23-01-2020 21:56:48 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE PROCEDURE [dbo].[sp_GenerateDimCalendar] @PY INT, @FY INT, @WeekStart INT, @Operation VARCHAR(20)
AS
BEGIN

--TRUNCATE TABLE [dbo].[#temp_Dim_Calendar]
------------Testing---------------
	/*SELECT @PY AS PerviousYear
		, @FY AS FutureYear
		, @WeekStart AS WeekStart
		, @Operation AS Operation*/
	IF OBJECT_ID ('dbo.#temp_Dim_Calendar', 'U') IS NOT NULL
	BEGIN
		DROP TABLE [dbo].[#temp_Dim_Calendar]
	END
	CREATE TABLE [dbo].[#temp_Dim_Calendar](
		[Grain] [varchar](15) NULL,
		[Number] [int] NULL,
		[Day] [varchar](10) NULL,
		[Year] [int] NULL,
		[StartPeriod] [date] NULL,
		[EndPeriod] [date] NULL,
		[OverLap] [int] NULL
	)

	SET @Operation = LOWER(@Operation)

	IF LOWER(@Operation) = 'deleteandinsert' or LOWER(@Operation) = 'upsert'
		PRINT 'Operation : ' + @Operation + CHAR(10) + '-------------';
	ELSE
		PRINT 'Operation is Invalid'
	END
	--PRINT N'WeekStartDayNum : ' + cast(@WeekStart AS VARCHAR(10))
	--PRINT N'FutureYearsCount : ' + cast(@FY AS VARCHAR(10))
	--PRINT N'PastYearsCount : ' + cast(@PY AS VARCHAR(10))
-------------Constants----------------------
DECLARE @minyear INT = DATEPART(YEAR, getDATE()) - @PY
DECLARE @maxyear INT = DATEPART(YEAR, getDATE()) + @FY


-------------- Master Iteration through Years -------------
DECLARE @proyear INT = @minyear
WHILE @proyear <= @maxyear
BEGIN
PRINT 'Processing year : ' + cast(@proyear AS VARCHAR(10))

DECLARE @stdt DATE = cast(cast(@proyear AS VARCHAR(5)) + '-01-01' AS DATE)
DECLARE @eddt DATE = cast(cast(@proyear AS VARCHAR(5)) + '-12-31' AS DATE)
------------- Daily Grain ----------------
	DECLARE @number INT = 0
	WHILE @number <= 366
	BEGIN
		INSERT INTO [dbo].[#temp_Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
		SELECT 'Daily' AS Grain
		, DATEPART(dayofyear, DATEs) AS Number
		, DATENAME(dw, DATEs) AS [Day]
		,DATEPART(year, DATEs) AS [Year]
		,DATEs AS StartPeriod
		,DATEs AS EndPeriod
		,Null AS Overlap
			FROM(
				SELECT FORMAT(DATEADD(day, @number, @stdt), 'yyyy-MM-dd') AS dates
				--SELECT DATEADD(day, number, @dt)
				WHERE DATEADD(day, @number, @stdt) <= @eddt
			) a
		SET @number=@number+1
	END
------------- Monthly Grain --------------
	DECLARE @promnth int = 1
	WHILE @promnth <= 12
	BEGIN
		DECLARE @som date = cast(cast(@proyear AS VARCHAR(5)) + '-' + cast(@promnth AS VARCHAR(2)) + '-01' AS DATE)
		DECLARE @eom date = EOMONTH(@som)
		INSERT INTO [dbo].[#temp_Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
		SELECT 'Monthly' AS Grain
		, @promnth AS Number
		, Null AS [Day]
		,@proyear AS [Year]
		,@som AS StartPeriod
		,@eom AS EndPeriod
		,Null AS Overlap
		SET @promnth=@promnth+1
	END
------------- Yearly Grain ---------------
	INSERT INTO [dbo].[#temp_Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
	SELECT 'Yearly' AS Grain
	, Null AS Number
	, Null AS [Day]
	,@proyear AS [Year]
	,@stdt AS StartPeriod
	,@eddt AS EndPeriod
	,Null AS Overlap
------------- Quarterly Grain ------------
	DECLARE @proqtr int = 0
	WHILE @proqtr < 12
	BEGIN
		SET @proqtr=@proqtr+1
		DECLARE @soq date = cast(cast(@proyear AS VARCHAR(5)) + '-' + cast(@proqtr AS VARCHAR(2)) + '-01' AS DATE)
		SET @proqtr=@proqtr+2
		DECLARE @soq1 date = cast(cast(@proyear AS VARCHAR(5)) + '-' + cast(@proqtr AS VARCHAR(2)) + '-01' AS DATE)
		DECLARE @eoq date = EOMONTH(@soq1)
		INSERT INTO [dbo].[#temp_Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
		SELECT 'Quarterly' AS Grain
		, @proqtr AS Number
		, Null AS [Day]
		,@proyear AS [Year]
		,@soq AS StartPeriod
		,@eoq AS EndPeriod
		,Null AS Overlap
	END
------------- Weekly Grain ---------------
	IF @WeekStart > 0 and @WeekStart < 8
	BEGIN
		SET DATEFIRST @WeekStart
	END
	DECLARE @proweek int =  1
	DECLARE @sow date = @stdt
	DECLARE @asow date = DATEADD(dd, -(DATEPART(dw, @sow)-1), @sow)
	DECLARE @eow date = DATEADD(dd, 7-(DATEPART(dw, @sow)), @sow)
	DECLARE @eoy date = @eddt
	DECLARE @overlap int = 0
	WHILE @proweek <= 53
	BEGIN
		IF @proweek = 1
		BEGIN
			IF DATEPART(MONTH, @asow) = DATEPART(MONTH, @eow)
			BEGIN
				SET @overlap = 0
			END
			ELSE
			BEGIN
				SET @overlap = 1
			END
		END
		ELSE
		BEGIN
			IF DATEPART(MONTH, @sow) = DATEPART(MONTH, @eow)
			BEGIN
				SET @overlap = 0
			END
			ELSE
			BEGIN
				SET @overlap = 1
			END 
		END
		IF @eow <= @eoy
		BEGIN
			SET @overlap = @overlap
		END
		ELSE
		BEGIN
			SET @eow = @eoy
		END
		IF @sow <= @eow
		BEGIN
			INSERT INTO [dbo].[#temp_Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
			SELECT 'Weekly' AS Grain
			, @proweek AS Number
			, Null AS [Day]
			,@proyear AS [Year]
			,@sow AS StartPeriod
			,@eow AS EndPeriod
			,@overlap AS Overlap
		END

		SET @sow = DATEADD(day, 1, @eow)
		SET @eow = DATEADD(day, 6, @sow)
		SET @proweek=@proweek+1
	END

SET @proyear = @proyear + 1
END
PRINT '--------------'
IF UPPER(@Operation) = 'DELETEANDINSERT'
BEGIN
	PRINT('Deleting and Inserting')
	TRUNCATE TABLE dbo.Dim_Calendar;
	INSERT INTO  dbo.Dim_Calendar (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
	SELECT * FROM [dbo].[#temp_Dim_Calendar]
END

IF UPPER(@Operation) = 'UPSERT'
BEGIN
	----------------- Update the Dim_Calendar with the new set of data -----------------
	PRINT('Performing Update\Insert Operation')
	UPDATE [dbo].[Dim_Calendar]
	SET Grain = temp.Grain,
		Number = temp.Number,
		Day = temp.Day,
		Year = temp.Year,
		StartPeriod = temp.StartPeriod,
		EndPeriod = temp.EndPeriod,
		Overlap = temp.Overlap
		FROM [dbo].[Dim_Calendar] ori
		INNER JOIN [dbo].[#temp_Dim_Calendar] temp
		on ori.[Grain] = temp.[Grain] and ori.[Year] = temp.[Year]
		WHERE temp.[Grain] = 'Yearly' -- Update only Yearly grain since join doesn't contain Number column in it

	UPDATE [dbo].[Dim_Calendar]
	SET Grain = temp.Grain,
		Number = temp.Number,
		Day = temp.Day,
		Year = temp.Year,
		StartPeriod = temp.StartPeriod,
		EndPeriod = temp.EndPeriod,
		Overlap = temp.Overlap
		FROM [dbo].[Dim_Calendar] ori
		INNER JOIN [dbo].[#temp_Dim_Calendar] temp
		ON ori.[Grain] = temp.[Grain] and ori.[Year] = temp.[Year] and ori.[Number] = temp.[Number]
		WHERE temp.[Grain] != 'Yearly'; -- Update everything except Yearly grain

	------------- Insert if the data is not there in the Dim_Calendar --------------
	INSERT INTO [dbo].[Dim_Calendar] (Grain, Number, Day, Year, StartPeriod, EndPeriod, Overlap)
			SELECT temp.[Grain],
			temp.[Number],
			temp.[Day],
			temp.[Year],
			temp.[StartPeriod],
			temp.[EndPeriod],
			temp.[Overlap]
			FROM [dbo].[#temp_Dim_Calendar] temp
			LEFT JOIN [dbo].[Dim_Calendar] ori
			on ori.[Number] = temp.[Number] and ori.[Grain] = temp.[Grain] and ori.[Year] = temp.[Year]
			WHERE ori.[Number] is NULL and ori.[Grain] is NULL and ori.[Year] is NULL and temp.[Grain] != 'Yearly' -- Data except Yearly grain since join cannot be performed for YYearly grain with Number column since it is NULL
		UNION
			SELECT temp.[Grain],
			temp.[Number],
			temp.[Day],
			temp.[Year],
			temp.[StartPeriod],
			temp.[EndPeriod],
			temp.[Overlap]
			FROM [dbo].[#temp_Dim_Calendar] temp
			LEFT JOIN [dbo].[Dim_Calendar] ori
			on ori.[Grain] = temp.[Grain] and ori.[Year] = temp.[Year]
			WHERE ori.[Number] is NULL and ori.[Grain] is NULL and ori.[Year] is NULL and temp.[Grain] = 'Yearly' -- Data only for Yearly grain
END
	PRINT '--------------'
	PRINT('STATUS : COMPLETED')
	DROP TABLE [dbo].[#temp_Dim_Calendar];
	PRINT '--------------'
GO


