define(function(){
    var upload_wrap =  function(post_url, fname_opt, fileid_opt, serial_opt, chunk_size_opt){
    $( function(){
      function handleDragOver(evt){
          evt.stopPropagation();
          evt.preventDefault();
          evt.dataTransfer.dropEffect = 'copy';
      };

      function handleFileSelect(evt) {
        evt.stopPropagation();
        evt.preventDefault();

        var files = evt.dataTransfer.files; // FileList object
        var progress = $('.percent');
        var loaded_total = 0;
        // files is a FileList of File objects. List some properties.
        var output = [];

        function updateProgress(e){
            if(e.lengthComputable){
                loaded_total = loaded_total + e.loaded;
                var percentLoaded = Math.round((loaded_total / file.size) * 100);
                if(percentLoaded < 100){
                    progress.css('width', percentLoaded + '%');
                    progress.text(percentLoaded + '%');
                }
            }
        }

        function uploadFile(file){
            // TODO: when file is tiny or even emply
            var self = this;

            function setupSender(blob, file_id, serial){
                var xhr = new XMLHttpRequest();
                this.xhr = xhr;
                xhr.open("POST", post_url);
                //xhr.open("POST", {{reverse_url('upload')}});
                xhr.overrideMimeType('text/plain; charset=x-user-defined-binary');
                xhr.responseType = 'json'
                // call when server return data
                xhr.upload.onprogress = updateProgress;
                xhr.onload = function(evt){
                    if(evt.lengthComputable){
                        var percentOnload = Math.round((loaded_total / file.size) * 100);
                        // magic number 97
                        if(percentOnload > 97){
                            progress.css('width', '100%');
                            progress.text('100%');
                        }
                    }
                };
                formdata = new FormData();
                sliced_file = new File([blob], escape(file.name), {type: file.type, lastModified: new Date()})
                formdata.append(fname_opt, sliced_file);
                //formdata.append("{{options.fname}}", sliced_file);
                formdata.append(fileid_opt, file_id);
                //formdata.append("{{options.fileid}}", file_id);
                formdata.append(serial_opt, serial);
                //formdata.append("{{options.serial}}", serial);
                xhr.send(formdata);
            }

            function getBlobSlice(file, start, end){
              if (file.webkitSlice) {
                  // file sliced in [start, end) format
                  var blob = file.webkitSlice(start, end);
              } else if (file.mozSlice) {
                  var blob = file.mozSlice(start, end);
              } else if(file.slice){
                  var blob = file.slice(start, end);
              }
              return blob;
            }

            // read all content into memory at one time
            var chunk_size = chunk_size_opt;
            //var chunk_size = {{options.chunk_size}};
            var full_chunk_loop_time = parseInt(file.size / chunk_size);
            var left_chunk_size = file.size % chunk_size;

            // file_id, should generated by the whole file, it should be the signature of one file
            // for example: read the first chunk and head of the rest chunks, merge the string together,then
            // generate one md5
            // file_id is the key point of uploading and downloading
            var file_id = function(file){
                var file_info = [file.name, file.size];
                return md5(file_info.join(''));
            }(file);

            for(serial=0; serial<full_chunk_loop_time; serial++){
              var blob = getBlobSlice(file, serial*chunk_size, (serial+1)*chunk_size);
              setupSender(blob, file_id, serial);
            }

            // handle chunk that left
            if(left_chunk_size){
              var blob = getBlobSlice(file, full_chunk_loop_time*chunk_size, file.size);
              setupSender(blob, file_id, full_chunk_loop_time);
            }
        }

        // upload sigle file
        file = files[0];
        output.push('<li><strong class="filename">', file.name, '</strong> (', file.type || 'n/a', ') - ',
                      file.size, ' bytes, last modified: ',
                      file.lastModifiedDate ? file.lastModifiedDate.toLocaleDateString() : 'n/a',
                      '</li>');

        // upload file
        $('#list').html('<ul>' + output.join('') + '</ul>');
        uploadFile(file);
      };

      var drop_zone= document.getElementById('drop_zone');
      drop_zone.addEventListener('dragover', handleDragOver, false);
      drop_zone.addEventListener('drop', handleFileSelect, false);

    });
    };
    return{
        upload_wrap:upload_wrap
    }
});
