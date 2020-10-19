@ECHO off

REM Get basename of simulation input file to build the solution filename.
SET SIMULATION_NAME=%~nx1
SET SIMULATION_NAME=%SIMULATION_NAME:~0,-19%
SET SOLUTION_FILE=%SIMULATION_NAME%.example_solution

REM Read the simulation file.
ECHO Opening the simulation file: %1
FOR /F "tokens=*" %%A IN (%1) DO (
  FOR /F "tokens=1* delims= " %%B IN ("%%A") DO (
    IF "%%B" == "Grid" (
      SET GRIDFILE=%%~C
      GOTO :read_geometry
    )
  )
)

REM Read the geometry file.
:read_geometry
ECHO Opening the geometry file: %GRIDFILE%
FOR /F "tokens=*" %%A IN (%GRIDFILE%) DO (
  FOR /F "tokens=1* delims=:" %%B IN ("%%A") DO (
    IF "%%B" == "Number of nodes" (
      SET NUM_NODES=%%C
      ECHO Number of nodes:%NUM_NODES%
      GOTO :run_model
    )
  )
)

REM Write a silly solution file.
:run_model
ECHO Running the model...
ECHO ###This is a solution file for Standard Interface Template.###> %SOLUTION_FILE%
FOR /L %%N IN (1,1,%NUM_NODES%) DO (
  ECHO 0.0>> %SOLUTION_FILE%
)

REM Echo some silly progress to stdout.
FOR /L %%N IN (0,2,100) DO (
  ECHO %% %%N
  REM Sleep for 1 second.
  ping 127.0.0.1 -n 2 > nul
)
ECHO DONE
