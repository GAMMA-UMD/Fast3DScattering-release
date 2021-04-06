send_mail = false;
if send_mail
    % User input
    source = '';              %from address (gmail)
    destination = '';              %to address (any mail service)
    myEmailPassword = '';                  %the password to the 'from' account
    
    %set up SMTP service for Gmail
    setpref('Internet','E_mail',source);
    setpref('Internet','SMTP_Server','smtp.gmail.com');
    setpref('Internet','SMTP_Username',source);
    setpref('Internet','SMTP_Password',myEmailPassword);
    % Gmail server.
    props = java.lang.System.getProperties;
    props.setProperty('mail.smtp.auth','true');
    props.setProperty('mail.smtp.socketFactory.class', 'javax.net.ssl.SSLSocketFactory');
    props.setProperty('mail.smtp.socketFactory.port','465');
end

freqs = [125, 250, 500, 1000];
for i = 1:length(freqs)
    poolobj = gcp('nocreate');
    delete(poolobj);
    maxsample = 200000;
    sim_freq = freqs(i);
    if send_mail
        sendmail(destination, ['Started preprocessing for frequency ' num2str(sim_freq)], [getenv('COMPUTERNAME') ' ' datestr(datetime('now'))]);
    end
    [input_list, pre_time] = generateBEMInputs(YOUR_LIST_OF_OBJECTS_IN_A_TXT_FILE,maxsample,'icosphere_order4_5m.obj',sim_freq);
    if send_mail
        sendmail(destination, ['Completed preprocessing for frequency ' num2str(sim_freq) ' in ' num2str(pre_time) 's'], [getenv('COMPUTERNAME') ' ' datestr(datetime('now'))]);
    end
    poolobj = gcp('nocreate');
    delete(poolobj);
    if send_mail
        sendmail(destination, ['Started simulation for frequency ' num2str(sim_freq)], [getenv('COMPUTERNAME') ' ' datestr(datetime('now'))]);
    end
    [output_list, sim_time] = runBEMscripts(input_list, sim_freq);
    savename = ['sim' num2str(sim_freq) '.mat'];
    save(savename);
    if send_mail
        sendmail(destination, ['Completed simulation for frequency ' num2str(sim_freq) ' in ' num2str(sim_time) 's'], [getenv('COMPUTERNAME') ' ' datestr(datetime('now'))], savename);
    end
end