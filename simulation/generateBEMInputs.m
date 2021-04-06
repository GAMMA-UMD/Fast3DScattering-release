function [input_list, expired] = generateBEMInputs(listfile, maxsample, fieldpath, freq)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here

% filelist = dir(fullfile(folderpath, '**\*.034.obj'));
fid = fopen(listfile);
filelist = textscan(fid, '%s', 'delimiter','\n');
filelist = filelist{1};
N = length(filelist);
if N > maxsample
    N = maxsample;
end
input_list = cell(N, 1);
ppm = ParforProgressbar(N, 'showWorkerProgress', true, 'progressBarUpdatePeriod', 5, 'parpool', {'local', 32});
tic
parfor i=1:N
    ppm.increment();
    [subfolder] = fileparts(filelist{i});
    objpath = filelist{i};
    inputfile = fullfile(subfolder, 'input.dat');
    input_list{i} = inputfile;
    copyfile('input.fmm', subfolder);
    try
%         generateBEMModelDirSource(objpath, fieldpath, [10,0,0], [freq,freq], inputfile, 1, 1, 0);
%         boundary condition 2:
        generateBEMModelDirSource(objpath, fieldpath, [10,0,0], [freq,freq], inputfile, 2, 0, 0); 
    catch
        delete(inputfile);
        delete(fullfile(subfolder, 'input.fmm'));
    end
end
expired = toc;
delete(ppm);
end

