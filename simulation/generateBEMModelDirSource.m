%GENERATEBEMMODEL Creats a model file for FastBEM
%% INPUT :
% input_filename            : .obj model containing scene objects ( BEM elements )
% input_field_filename      : .obj model containing points on which pressure field is evaluated
% src_pos                   : source position
% freq                      : frequnecy of BEM simulation
% SHcoeffs                  : spherical harmnonic coeffs. for directional source
% output_model_filename     : .dat file that stores the BEM information
% output_src_filename       : .inc file that stores the directional source information
% output_src_pos_filename   : .pos file that stores the source position
% bc_type                   : type of boundary condition,  1 = pressure is given
%                                                          2 = normal velocity is given
%                                                          3 = specific impedence is given
% bc_value                  : complex number for the value of boundary condition
%% USAGE :
% generateBEMModelDirSource('L:\GAMMA18_data\G\project_esm\Sound\models\blackbox\feature_demo\Wall\BEM_model\model_only_200Hz.obj',...
%                          'L:\GAMMA18_data\G\project_esm\Sound\models\blackbox\feature_demo\Wall\BEM_model\wall_listener_quad.obj', ...
%                          [-10.463519 -1.533231 1.5], 180, [ 1 0 0 1], ...
%                          'input.dat', 'input.inc', 'input.pos' );
function [ ] = generateBEMModelDirSource( input_filename, input_field_filename, ...
    src_pos, freq, output_model_filename, bc_type, bc_value, modeNo )

c = 343.0;
nCores = 8;
%% read the obj model
% OBJ = read_wobj_BEM(input_filename);
% N = length(OBJ.objects);
% assert(N == 1); % currently only handling the 'f' type objects
% if(OBJ.objects(3).type == 'f')
%     Fs = OBJ.objects(3).data.vertices;
%     Vs = OBJ.vertices;
    [Vs, Fs] = loadawobj(input_filename);
    indices = Fs';
    vertices = Vs';
    S = size(vertices);
    NumVertices = S(1);
    
    S = size(indices);
    NumIndices = S(1);
    ElementSize = S(2);
    assert(ElementSize == 3);   % to check if its a triangle
    
    % compute center vertex and face normals assuming that elements are triangles
    centerVertices = zeros(NumIndices,3);
    faceNormals = zeros(NumIndices,3);
    for i=1:1:NumIndices
        index_1 = indices(i,1);     index_2 = indices(i,2);     index_3 = indices(i,3);
        % compute center vertex
        centerVertices(i,:) = (vertices(index_1,:) + vertices(index_2,:) + vertices(index_3,:))/3.0;
        % compute face normal
        side_1 = vertices(index_1,:) - vertices(index_2,:);
        side_2 = vertices(index_3,:) - vertices(index_2,:);
        normal = cross(side_2,side_1);
        magnormal = norm(normal,2);
        %             if(magnormal > 1e-6 )
        if(magnormal > 1e-7 )
            normal = normal/magnormal;
        else
            fprintf('Face %d has zero normal   %f', i, magnormal);
            assert(false);
        end
        faceNormals(i,:) = normal;
    end
    S = size(faceNormals);
    NumFaceNormals = S(1);
% end


%% read the file with field information
[Vf, Ff] = loadawobj(input_field_filename);
% OBJ_field = read_wobj(input_field_filename);
% N_field = length(OBJ_field.objects);
% assert(N_field == 1); % currently only handling the 'f' type objects
% if(OBJ_field.objects(3).type == 'f')
    indices_field = Ff'; %OBJ_field.objects(3).data.vertices;
    vertices_field = Vf'; %OBJ_field.vertices;
    
    S = size(indices_field);
    NumIndices_field = S(1);
    
    S = size(vertices_field);
    NumVertices_field = S(1);
    
    % compute vertex normals
    vertexNormals_field = zeros(NumVertices_field,3);
    for i=1:1:NumIndices_field
        index_1 = indices_field(i,1);       index_2 = indices_field(i,2);       index_3 = indices_field(i,3);
        % compute face normal
        side_1 = vertices_field(index_1,:) - vertices_field(index_2,:);
        side_2 = vertices_field(index_3,:) - vertices_field(index_2,:);
        normal = cross(side_2,side_1);
        normal = normal/norm(normal,2);
        % compute vertex normal
        vertexNormals_field(index_1,:) = vertexNormals_field(index_1,:) + normal;
        vertexNormals_field(index_2,:) = vertexNormals_field(index_2,:) + normal;
        vertexNormals_field(index_3,:) = vertexNormals_field(index_3,:) + normal;
    end
    % normalize
    for i=1:1:NumVertices_field
        magnormal = norm(vertexNormals_field(i,:),2);
        if(magnormal > 1e-4 )
            vertexNormals_field(i,:) = vertexNormals_field(i,:)/magnormal;
        end
    end
    %     end
    
    %% calculate the velocity values for neumann boundary condition
    
%     if(bc_type == 2)
%         vertexNormals_object = zeros(NumVertices,3);
%         vertices_obj = OBJ.vertices;
%         for i = 1:NumIndices
%             index_1 = indices(i,1);       index_2 = indices(i,2);       index_3 = indices(i,3);
%             side_1 = vertices_obj(index_1,:) - vertices_obj(index_2,:);
%             side_2 = vertices_obj(index_3,:) - vertices_obj(index_2,:);
%             normal = cross(side_2,side_1);
%             normal = normal/norm(normal,2);
%             % compute vertex normal
%             vertexNormals_object(index_1,:) = vertexNormals_object(index_1,:) + normal;
%             vertexNormals_object(index_2,:) = vertexNormals_object(index_2,:) + normal;
%             vertexNormals_object(index_3,:) = vertexNormals_object(index_3,:) + normal;
%             
%         end
%         bc_value_at_vertices = neumannBoundaryCondition(Ut(:, modeNo), vertexNormals_object, freq);
%         
%         for i = 1:NumIndices
%             index_1 = indices(i,1);       index_2 = indices(i,2);       index_3 = indices(i,3);
%             bc_value(i) = (bc_value_at_vertices(index_1) + bc_value_at_vertices(index_2) + bc_value_at_vertices(index_3))/3.0;
%         end
%         
%         bc_value = bc_value';
%     end
    
    %% write the BEM model format
    fid  = fopen(output_model_filename, 'w');
    
    fprintf(fid, 'Ellipsoid model for testing BEM scattering \n'); % comment
    fprintf(fid, '   Complete 2 %d\n', nCores);   % ! Job Type (Complete/Field Only); Solver Type (1=FMM/2=ACA BEM/3=CBEM, New in V.2.8.0), No. Threads
    fprintf(fid, '   Full 0 0.0\n');  % ! Problem Space, Symmetry Plane, Symmetry Plane Property RHCoef (=1 for Rigid; =-1 for Soft)
    fprintf(fid, '   %d %d %d %d 1\n', NumIndices, NumVertices, NumVertices_field, NumIndices_field); % ! Nos. of Boundary Elements/Nodes and Field Points/Cells
    
    fprintf(fid, '   %d %d\n', 1, 0);   % ! No. of plane incident waves (nplane), User defined sources (1=Yes/0=No)
    %     fprintf(fid, '   0 0\n');             % ! No. of monopole sources, and no. of dipole sources
    %     fprintf(fid, '   %d %d\n', 1, 0);   % ! No. of plane incident waves (nplane), User defined sources (1=Yes/0=No)
    %fprintf(fid, '   1 0\n');             % ! No. of monopole sources, and no. of dipole sources
    fprintf(fid, '   (1.0, 0.0) %f %f %f\n', -src_pos(1)/norm(src_pos), -src_pos(2)/norm(src_pos), -src_pos(3)/norm(src_pos)); % ! Complex amplitude and direction vector of point sources
    fprintf(fid, '   0 0\n');             % ! No. of monopole sources, and no. of dipole sources
    fprintf(fid, '   %f 1.29 2.0E-5 1.0E-12 0.\n', c); %  ! cspeed (c), density (rou), reference sound pressure, reference intensity, wavenumber k ratio
    fprintf(fid, '   %f %f 0 1 0\n', freq(1), freq(2)); % !  Freq1, Freq2, No. freqs, NOctaveUpdate BCs for each frequency (1=Yes/0=No)
    fprintf(fid, '   0 3 1 0 One\n'); % !  Use of HBIE (1=Yes, 0=No), nruleb, nrulef, animation (1=Yes, 0=No), Tecplot data (All/One)
    
    fprintf(fid, ' $ Nodes:\n');
    for i=1:1:NumVertices
        fprintf(fid, '   %d %f %f %f\n', i, vertices(i,1), vertices(i,2), vertices(i,3) );
    end
    
    fprintf(fid, ' $ Elements and Boundary Conditions:\n');
    for i=1:1:NumIndices
        fprintf(fid, '   %d %d %d %d %d (%f, %f) 1\n', i, indices(i,1), indices(i,2), indices(i,3), bc_type, real(bc_value), imag(bc_value) );
    end
    
    fprintf(fid, ' $ Field Points:\n');
    for i=1:1:NumVertices_field
        fprintf(fid, '   %d %f %f %f\n', i, vertices_field(i,1), vertices_field(i,2), vertices_field(i,3) );
    end
    
    fprintf(fid, ' $ Field Cells:\n');
    for i=1:1:NumIndices_field
        fprintf(fid, '   %d %d %d %d %d\n', i, indices_field(i,1), indices_field(i,2), indices_field(i,3), indices_field(i,3) ); %We're using triangular meshes for listener positions..
    end
    
    fprintf(fid, ' $ End of the File\n');
    fclose(fid);
    
    
    
    %% write the source file
    % write data in file
    %     fid  = fopen(output_src_filename, 'w');
    %     fprintf(fid, 'Incident Field at Frequency No.: 1\n');
    %
    %     numSHcoeffs = length(SHcoeffs);
    %     nSH = sqrt(numSHcoeffs);
    %
    %     % find k
    %     K = 2*pi*freq/c;
    %
    %     % evaluate source pressure at boundary positions
    %     SourcePresBpoint = zeros(NumIndices,1);
    %     for lSH=0:1:nSH-1
    %         for mSH=-lSH:1:lSH
    %             indexSH = lSH*(lSH+1) + mSH + 1;
    %             pressure = evaluateSHSource(src_pos, lSH, mSH, centerVertices, K);
    %             SourcePresBpoint = SourcePresBpoint + (SHcoeffs(indexSH) * pressure);
    %         end
    %     end
    %     % evaluate source pressure gradident at boundary positions in direction of face normals
    %     SourcePresGradBpoint = zeros(NumIndices,1);
    %     for lSH=0:1:nSH-1
    %         for mSH=-lSH:1:lSH
    %             indexSH = lSH*(lSH+1) + mSH + 1;
    %             pressureGrad = evaluateSHSourceGradient(src_pos, lSH, mSH, centerVertices, K);
    %             pressureGradNormal = dot(pressureGrad, faceNormals, 2); % dot product with normal
    %             SourcePresGradBpoint = SourcePresGradBpoint + (SHcoeffs(indexSH) * pressureGradNormal);
    %         end
    %     end
    % %     % NOTE : convert to monopole source
    % %     SourcePresBpoint = 1i*SourcePresBpoint;
    % %     SourcePresGradBpoint = 1i*SourcePresGradBpoint;
    %
    %     fprintf(fid, 'Boundary element, phi_inc, q_inc:\n');
    %     for i=1:1:NumIndices
    %        fprintf(fid, '%d (%f,%f) (%f,%f)\n', i,   real(SourcePresBpoint(i)), imag(SourcePresBpoint(i)), ...
    %                                                  real(SourcePresGradBpoint(i)), imag(SourcePresGradBpoint(i)) );
    %     end
    %
    %
    %
    %     % evaluate source pressure at field points
    %     SourcePresFpoint = zeros(NumVertices_field,1);
    %     for lSH=0:1:nSH-1
    %         for mSH=-lSH:1:lSH
    %             indexSH = lSH*(lSH+1) + mSH + 1;
    %             pressure = evaluateSHSource(src_pos, lSH, mSH, vertices_field, K);
    %             SourcePresFpoint = SourcePresFpoint + (SHcoeffs(indexSH) * pressure);
    %         end
    %     end
    %     % evaluate source pressure gradient at field points in direction of vertex normals
    %     SourcePresGradFPoint = zeros(NumVertices_field,1);
    %     for lSH=0:1:nSH-1
    %         for mSH=-lSH:1:lSH
    %             indexSH = lSH*(lSH+1) + mSH + 1;
    %             pressureGrad = evaluateSHSourceGradient(src_pos, lSH, mSH, vertices_field, K);
    %             pressureGradNormal = dot(pressureGrad, vertexNormals_field, 2); % dot produce with normal
    %             SourcePresGradFPoint = SourcePresGradFPoint + (SHcoeffs(indexSH) * pressureGradNormal);
    %         end
    %     end
    %% this gives total field
    %     % NOTE : convert to monopole source
    %     SourcePresFpoint = 1i*SourcePresFpoint;
    %     SourcePresGradFPoint = 1i*SourcePresGradFPoint;
    %     % NOTE : BEM pressure and monopole source pressure have real and imaginary part inverted.
    %     % Invert the BEM pressure here so that it adds correctly with source pressure specified later
    %     SourcePresFpoint = 1i*real(SourcePresFpoint) + imag(SourcePresFpoint);
    %     SourcePresGradFPoint = 1i*real(SourcePresGradFPoint) + imag(SourcePresGradFPoint);
    
    % NOTE : BEM pressure and directional source pressure have real and imaginary part inverted with a minus sign.
    % Invert the BEM pressure here so that it adds correctly with source pressure specified later
    %     SourcePresFpoint = -1i*real(SourcePresFpoint) - imag(SourcePresFpoint);
    %     SourcePresGradFPoint = -1i*real(SourcePresGradFPoint) - imag(SourcePresGradFPoint);
    %
    %     fprintf(fid, 'Field point, phi_inc, q_inc:\n');
    %     for i=1:1:NumVertices_field
    %         fprintf(fid, '%d (%f,%f) (%f,%f)\n', i, real(SourcePresFpoint(i)), imag(SourcePresFpoint(i)), ...
    %                                                 real(SourcePresGradFPoint(i)), imag(SourcePresGradFPoint(i)) );
    %     end
    %     fclose(fid);
    
    % %%  this gives scattered field
    %     fprintf(fid, 'Field point, phi_inc, q_inc:\n');
    %     for i=1:1:NumVertices_field
    %         fprintf(fid, '%d (%f,%f) (%f,%f)\n', i, 0.0, 0.0, ...
    %                                                 0.0, 0.0 );
    %     end
    %     fclose(fid);
    
    %     fid = fopen(output_src_pos_filename, 'w');
    %     fprintf(fid, '%f %f %f', src_pos(1), src_pos(2), src_pos(3));
    %     fclose(fid);
    
    %     save('SourcePressure.mat', 'SourcePresFpoint');
    
    
    %     figure;
    %     plot3(src_pos(1), src_pos(2), src_pos(3), 'o', 'MarkerFaceColor', 'r', 'MarkerSize',10);
    %     hold on
    %     scatter3(centerVertices(:,1), centerVertices(:,2), centerVertices(:,3), 50*ones(NumIndices,1), abs(SourcePresBpoint), 'filled');
    %     hold on
    %     scatter3(vertices_field(:,1), vertices_field(:,2), vertices_field(:,3), 50*ones(NumVertices_field,1), abs(SourcePresFpoint), 'filled');
    %     hold on
    %     quiver3(centerVertices(:,1), centerVertices(:,2), centerVertices(:,3),faceNormals(:,1),faceNormals(:,2),faceNormals(:,3))
    %     hold on
    %     quiver3(vertices_field(:,1), vertices_field(:,2), vertices_field(:,3),vertexNormals_field(:,1), vertexNormals_field(:,2), vertexNormals_field(:,3));
    %     hold on
    %     set(gca,'DataAspectRatio',[1 1 1])
    %     set(gcf, 'Renderer', 'opengl')
    %
    %     figure;
    %     plot3(src_pos(1), src_pos(2), src_pos(3), 'o', 'MarkerFaceColor', 'r', 'MarkerSize',10);
    %     hold on
    %     scatter3(centerVertices(:,1), centerVertices(:,2), centerVertices(:,3), 50*ones(NumIndices,1), abs(SourcePresGradBpoint), 'filled');
    %     hold on
    %     scatter3(vertices_field(:,1), vertices_field(:,2), vertices_field(:,3), 50*ones(NumVertices_field,1), abs(SourcePresGradFPoint), 'filled');
    %     hold on
    %     set(gca,'DataAspectRatio',[1 1 1])
    %     set(gcf, 'Renderer', 'opengl')
end

