function logout() {
    $.removeCookie('kunciRahasia', { path: '/' })
    Swal.fire({
        title: "Anda telah logout",
        text: "Kami menanti kedatanganmu kembali 😊",
        icon: "success",
        showConfirmButton: false,
        timer: 3000
    });
    
    // Menunda pengalihan halaman selama 3 detik
    setTimeout(function () {
        window.location.href = '/halaman_login';
    }, 3000);
}


function tambah(){
    let nama = $("#nama").val()
    let resi = $("#resi").val()
    if( nama && resi){
        $.ajax({
            type : "POST",
            url : "/tambahPaket",
            data : {name_give : nama, resi_give : resi},
            success : function(response){
                if (response['result'] === "success"){
                    Swal.fire({
                        title: response['msg'],
                        icon: "success",
                        showConfirmButton: false,
                        timer: 3000
                    });
                    // Menunda pengalihan halaman selama 3 detik
                    setTimeout(function () {
                    window.location.href='/'
                    }, 3000);
                }
            }
        })
    }
    else {
        Swal.fire({
            title: "Maaf, nama dan resi paket tidak boleh kosong!",
            icon: "warning",
            showConfirmButton: false,
            timer: 2000
        });
    }
}


function edit(id){
    let id_paket = id
    let nama = $(`#nama${id_paket}`).val()
    let resi = $(`#resi${id_paket}`).val()
    if(nama && resi){
            $.ajax({
                type : "POST",
                url : "/editPaket",
                data : {id_give : id_paket, name_give : nama, resi_give : resi},
                success : function(response){
                    if (response['result'] === "success"){
                        Swal.fire({
                            title: response['msg'],
                            icon: "success",
                            showConfirmButton: false,
                            timer: 3000
                        });
                        // Menunda pengalihan halaman selama 3 detik
                        setTimeout(function () {
                        window.location.reload()
                        }, 3000);
                    }
                }
            })
    } 
    else {
        Swal.fire({
            title: "Maaf, nama dan resi paket tidak boleh kosong!",
            icon: "warning",
            showConfirmButton: false,
            timer: 2000
        });
    }
}

function hapus(id, nama){
    let id_paket = id
    let nama_paket = nama
            Swal.fire({
                title: `Anda akan menghapus ${nama_paket}!`,
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: `Ya, hapus!`
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        type: 'POST',
                        url: '/deletePaket',
                        data: { id_give: id_paket },
                        success: function (response) {
                            if (response['result'] === 'success') {
                                Swal.fire({
                                    title: "Deleted!",
                                    text: `Paket ${nama_paket} Telah Dihapus`,
                                    icon: "success",
                                    showConfirmButton: false,
                                    timer: 2000
                                });
                                // Menunda pengalihan halaman selama 3 detik
                                setTimeout(function () {
                                    window.location.reload()
                                }, 2000);
                            }
                        }
                    })
                }
            });
}

function search(keyword){
    // let search_word = keyword
    // console.log(search_word)
    // $.ajax({
    //     type: "GET",
    //     url : `/search?keyword=${keyword}`,
    //     data: {},
    //     success : function(response){
    //         if(response['result'] === "Not Found"){
    //             (".list-paket").toggleClass("d-none")
    //             (".card-notFound").toggleClass("d-none")
    //         }
    //     } 
    // })
    window.location.href=`/?keyword=${keyword}`
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        let search1 = $('#search1').val()
        let search2 = $('#search2').val()
        if(search1){
            search(search1)
        }
        else{
            search(search2)

        }
    }
}

function openBox() {
        $.ajax({
            type: "POST",
            url: "/openBox",
            data: { status : "True"},
            success: function (response) {
                if (response['result'] === "success") {
                    Swal.fire({
                        title: "Permintaan Telah Dikirim",
                        icon: "success",
                        showConfirmButton: false,
                        timer: 2000
                    });
                }
            }
        })
    
    }