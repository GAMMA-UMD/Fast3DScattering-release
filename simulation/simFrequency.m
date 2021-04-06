function [sim_times] = simFrequency(objpath, fieldpath, outputpath)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

%% Generate BEM scripts
freqs = [125, 250, 500, 1000, 2000, 4000, 8000];
N = length(freqs);
input_list = cell(N, 1);
[filepath,name,ext] = fileparts(objpath);
outputpath = fullfile(outputpath, name);
if ~exist(outputpath, 'dir')
       mkdir(outputpath)
end
sim_times = zeros(N, 1);
max_trial = 5;
for i=1:N   
    freq = freqs(i);
    inputfile = fullfile(outputpath, 'input.dat');
    input_list{i} = inputfile;
    copyfile('input.fmm', outputpath);
    try
        generateBEMModelDirSource(objpath, fieldpath, [10,0,0], [freq,freq], inputfile, 2, 0, 0);
    catch
        delete(inputfile);
        delete(fullfile(subfolder, 'input.fmm'));
        disp('simulation creation failed!');
        return;
    end
    
    % Run simulation
    tic
    output_file = fullfile(outputpath, 'output_result.dat');
    plt_file = fullfile(outputpath, 'output_tecplot.plt');
    output_name = ['output_result.' num2str(freq) '.dat'];
    plt_name = ['output_tecplot.' num2str(freq) '.plt'];
    desired_file =  fullfile(outputpath, output_name);
    desired_plt = fullfile(outputpath, plt_name);
    cmd = ['echo "' outputpath '" | FastBEM_Acoustics.exe'];
    try
        system(cmd);
        cnt = 1;
        while contains(fileread(output_file), 'NaN') && (cnt < max_trial)
            system(cmd);
            cnt = cnt + 1;
        end
        movefile(output_file, desired_file);
        movefile(plt_file, desired_plt);
    catch
        delete(output_file);
        disp('simulation failed!')
        return;
    end
    sim_times(i) = toc;
end

end

