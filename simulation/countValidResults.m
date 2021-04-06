function [cnt] = countValidResults(filelist)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
% fid = fopen(listfile);
% filelist = textscan(fid, '%s', 'delimiter','\n');
% filelist = filelist{1};
N = length(filelist);
valid_cnt = zeros(N, 1);
% h = waitbar(0,'Initializing waitbar...');

ppm = ParforProgressbar(N, 'showWorkerProgress', true, 'progressBarUpdatePeriod', 5, 'parpool', {'local', 32});
tic
parfor i=1:N
    ppm.increment();
%     perc = i/N;
%     waitbar(perc,h,sprintf('%f%% along...', perc*100));
    try
        if ~isfile(filelist{i})
            continue;
        end
        [subfolder] = fileparts(filelist{i});
        if ~contains(fileread(filelist{i}), 'NaN')
            valid_cnt(i) = 1;
        else
            delete(fullfile(subfolder, 'output_result.125.dat'));
            delete(fullfile(subfolder, 'output_freq_responses.plt'));
            delete(fullfile(subfolder, 'output.log'));
            delete(fullfile(subfolder, 'input.dat'));
        end
    catch
        disp(['please check file ' num2str(i)]);
    end
end
toc
% close(h)
delete(ppm);
cnt = sum(valid_cnt);
disp([num2str(sum(valid_cnt)) '/' num2str(N) ' results are valid']);
end

