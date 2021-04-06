function [output_list, expired] = runBEMscripts(filelist, freq)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
% fid = fopen(listfile);
% filelist = textscan(fid, '%s', 'delimiter','\n');
% filelist = filelist{1};
N = length(filelist);
output_list = cell(N, 1);
ppm = ParforProgressbar(N, 'showWorkerProgress', true, 'progressBarUpdatePeriod', 5, 'parpool', {'local', 8});
tic
parfor i=1:N
    ppm.increment();
    [subfolder] = fileparts(filelist{i});
    output_file = fullfile(subfolder, 'output_result.dat');
%     output_name = ['output_result.' num2str(freq) '.dat'];
    output_name = ['output_result.' num2str(freq) '.bc2.dat'];
    desired_file =  fullfile(subfolder, output_name);
    if isfile(desired_file)
        disp(['skipping directory ' subfolder]);
        output_list{i} = desired_file;
        continue;
    end
    cmd = ['echo "' subfolder '" | FastBEM_Acoustics.exe'];
    try
        system(cmd);
        movefile(output_file, desired_file);
        output_list{i} = desired_file;
        disp(['result saved to ' desired_file]);
        if isfile(desired_file)
            if contains(fileread(desired_file), 'NaN')
                delete(desired_file);
                delete(fullfile(subfolder, 'output_freq_responses.plt'));
                delete(fullfile(subfolder, 'output.log'));
                delete(fullfile(subfolder, 'input.dat'));
            end
        end
    catch
        delete(output_file);
    end
    delete(fullfile(subfolder, 'output_tecplot.plt'));
end
expired = toc;
delete(ppm);
end

