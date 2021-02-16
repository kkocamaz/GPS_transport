function TR_plot(loc_real,T_real,loc_aug,T_aug,segments,arac_name)
    persistent n
    if isempty(n)
        n = 200;
    end
    n = n+1;
    
    figure(n)
%     fig_arac_id=10;
%     loc_real = logical(T_real.arac_id==T_arac.arac_cats(fig_arac_id));
%     loc_aug = logical(T_aug.arac_id==T_arac.arac_cats(fig_arac_id));
    s1=geoscatter(T_real.lat(loc_real),T_real.lon(loc_real),60,'red','filled');
    s1.DataTipTemplate.DataTipRows(3)=dataTipTextRow('Time',cellstr(datestr(T_real.time(loc_real))));
    s1.DataTipTemplate.DataTipRows(1:end-1)=[];
    hold on
    s2=geoscatter(T_aug.lat(loc_aug),T_aug.lon(loc_aug),120,'black');
    s2.DataTipTemplate.DataTipRows(3)=dataTipTextRow('Time',cellstr(datestr(T_aug.time(loc_aug))));
    hold on
    s3=geoscatter(segments.startLat(segments.dir==1),segments.startLon(segments.dir==1),90,'s','blue'); %start
    hold on
    s4=geoscatter(segments.endLat(segments.dir==1),segments.endLon(segments.dir==1),15,'s','blue','filled'); %end
    hold on
    s5=geoscatter(segments.startLat(segments.dir==2),segments.startLon(segments.dir==2),90,'s','blue'); %start
    hold on
    s6=geoscatter(segments.endLat(segments.dir==2),segments.endLon(segments.dir==2),15,'s','blue','filled'); %end
    geobasemap streets
    legend('real','aug','segments start','segments end')
    title(['arac id ',arac_name]);


%     text(T_real.lat(loc_real),T_real.lon(loc_real),num2str(T_real.time_num(loc_real)))
end
